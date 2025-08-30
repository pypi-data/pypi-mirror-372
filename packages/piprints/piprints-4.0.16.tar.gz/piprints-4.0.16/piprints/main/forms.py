from datetime import date, time

from piprints.main.models import * # mantenere qui! CharField viene ridefinito piu' sotto...

from django.utils.safestring import mark_safe
from django.forms import Form, ModelForm
from django.forms.utils import ValidationError, flatatt
from django.forms.fields import Field, CharField, EmailField, FileField
from django import forms
from django.forms.widgets import Widget, Select
from django.forms.models import modelform_factory, modelformset_factory
from django.db.models.fields import DateField, TimeField
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.db import models


## modificata dai file di libreria
from piprints.settings import BASE_ROOT


def strip_leading(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        return s

def strip_trailing(s, suffix):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    else:
        return s


def model_to_dict(instance, fields=None, exclude=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    # avoid a circular import
    from django.db.models.fields.related import ManyToManyField
    opts = instance._meta
    data = {}
    for f in opts.fields + opts.many_to_many:
        if not f.editable:
            continue
        if fields and not f.name in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if f.name == 'authors':
            assert isinstance(instance,Paper)
            data[f.name] = [x.person for x in PaperAuthor.objects.filter(
                paper = instance)]
        else:
            data[f.name] = f.value_from_object(instance)

    return data

class ManyToManyWidget(Widget):
    """
    A widget to input a list of Many2Many fields
    """
    fields = None # list of names of fields of related model

    def value_from_datadict(self, data, files, name):
        n = 0
        d={}
        for field in self.fields:
            l = data.getlist(name+'_'+field)
            d[field] = l
            n = max(n, len(l))

        l=[{} for i in range(n)]
        for i in range(n):
            for field in self.fields:
                l[i][field] = d[field][i]
        return l

    def field_html(self, attrs):
        return '<input%s />' % flatatt(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        """
        value is expected to be a list of dictionaries of values
        for the related Model
        """
        final_attrs = self.build_attrs(attrs)
        if not value:
            value = [{}]
        html = '<table>'
        if len(self.fields)>1:
            html += '<tr>'
            for field in self.fields:
                html += '<th>%s</th>' % field
            html += '</tr>'
        for val in value:
            html += '<tr>'
            for field in self.fields:
                final_attrs['name']=name+'_'+field
                if type(val) == dict:
                    vv = val.get(field,'')
                else:
                    vv = getattr(val,field)
                final_attrs['value'] = vv
                html += '<td>%s</td>\n' % self.field_html(final_attrs)
#                html += '<td><input%s /></td>\n' % flatatt(final_attrs)
            html += '</tr>'

        html += '<tr><td><input class="adder" type="button" value="ADD"></td></tr>\n'
        html += '</table>\n'
        return mark_safe(html)

class ManyToManyInputField(Field):
    """
    A Field which selects a list of foreign model objects
    """
    widget = ManyToManyWidget
    Model = None # must be extended to fix a referencing model
    fields = ['value'] # fields of external model

    def clean(self, value):
        """
        Returns a list of objects of type Model
        if any object is new, it is not saved
        """
        objects = []
        for v in value:
            if not v:
                continue
            f = {}
            empty = True
            for field in self.fields:
                f[field] = v[field]
                if v[field]:
                    empty = False
            if empty:
                continue
            l = self.Model.objects.filter(**f)
            if not l:
                obj = self.Model()
                for field in self.fields:
                    setattr(obj,field,v[field])
                try:
                    obj.full_clean()
                except ValidationError as e:                    
                    if hasattr(e, 'error_dict'):
                        msg = ', '.join("{}: {}".format(key,', '.join(x for x in val)) for key,val in e)
                        e = ValidationError(msg)
                    raise e
            else:
                obj = l[0]
            objects.append(obj)
        if not objects and self.required:
            raise ValidationError('This field cannot be empty')
        return objects

class KeywordsWidget(ManyToManyWidget):
    fields = ['name']

class KeywordsInputField(ManyToManyInputField):
    widget = KeywordsWidget
    Model = Keyword
    fields = widget.fields

class TagsWidget(ManyToManyWidget):
    fields = ['value']

    def field_html(self, attrs):
        attrs = dict(attrs)
        value = attrs.pop('value')
        html = '<select%s />' % flatatt(attrs)
        html += '<option value="">------</option>'
        for tag in Tag.objects.all():
            selected = ' selected="1"' if tag.value == value else ''
            html += '<option value="{}"{}>{}</option>'.format(tag.value, selected, tag.value)
        html += '</select>'
        return html

class TagsInputField(ManyToManyInputField):
    widget = TagsWidget
    Model = Tag
    fields = ['value']

class LinksWidget(ManyToManyWidget):
    fields = ['url','description']

class LinksInputField(ManyToManyInputField):
    widget = LinksWidget
    Model = Link
    fields = widget.fields

class PersonsWidget(Widget):
    """
    A widget to input a list of (lastname,firstname) couples
    """

    suffix = ('_ln','_fn')

    def value_from_datadict(self, data, files, name):
        lastnames = data.getlist(name+self.suffix[0])
        firstnames = data.getlist(name+self.suffix[1])
        authors=[(lastnames[i],firstnames[i])
                 for i in range(min(len(lastnames),len(firstnames)))]
        return authors

    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(attrs)
        classes = final_attrs.get('class')
        if classes:
            classes = classes.split(' ')
        else:
            classes = []
        classes += ["autocomplete"]
        final_attrs['class'] = ' '.join(classes)
        if not value:
            value = [('','')]
        html = '<table><tr><th>lastname</th><th>firstname</th></tr>\n'
        for item in value:
            try:
                (lastname,firstname) = item
            except TypeError:
                lastname = item.lastname
                firstname = item.firstname
            final_attrs['name']=name+self.suffix[0]
            final_attrs['value']=lastname
            final_attrs['class']=' '.join(classes + ["lastname"])
            html += '<tr><td><input%s /></td>' % flatatt(final_attrs)
            final_attrs['name']=name+self.suffix[1]
            final_attrs['value']=firstname
            final_attrs['class']=' '.join(classes + ["firstname"])
            html += '<td><input%s /></td></tr>\n' % flatatt(final_attrs)
        html+='<tr><td><input class="adder" type="button" value="ADD PERSON"></td></tr>\n'
        html+='</table>\n'
        return mark_safe(html)

class PersonsField(Field):
    widget = PersonsWidget

    def clean(self, value):
        """
        Returns a list of Person objects.
        Possible new Persons have not been saved
        """

        authors = []
        order = 1
        for (lastname, firstname) in value:
            if lastname=='' and firstname=='':
                continue
            if lastname=='' or firstname=='':
                raise ValidationError("You must provide both lastname and firstname")
            l = Person.objects.filter(lastname__iexact=lastname, firstname__iexact=firstname)
            if l:
                ## se ce ne sono molti prende il primo senza battere ciglio
                author = l[0]
            else:
                author = Person(lastname=lastname, firstname=firstname)
            author.order = order
            order += 1
            authors.append(author)
        if not authors and self.required:
            raise ValidationError("You must provide at least one person")
        return authors

class InputWithAutocompleteWidget(Widget):
    """
    A widget to input a field with both a select with some possible
    choices and a free input to insert other values
    """

    autocomplete_url = 'override-this'

    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(attrs)
        classes = final_attrs.get('class')
        if classes:
            classes = classes.split(' ')
        else:
            classes = []
        classes.append('autocomplete_list')
        final_attrs['name'] = name
        final_attrs['value'] = value
        final_attrs['class'] = ' '.join(classes)
        final_attrs['autocomplete_url'] = self.autocomplete_url
        html = '<input%s />\n' % flatatt(final_attrs)
        return mark_safe(html)

class PaperTypeWidget(InputWithAutocompleteWidget):
    autocomplete_url = '/autocomplete/paper_type/'

class PaperTypeField(CharField):
    widget = PaperTypeWidget

class PositionWidget(InputWithAutocompleteWidget):
    autocomplete_url = '/autocomplete/position/'

class PositionField(CharField):
    widget = PositionWidget

class TimeWidget(Widget):
    """
    A widget to enter a date
    """
    suffixes = ('_h','_m')
    def __init__(self, attrs=None, format=None):
        super(TimeWidget, self).__init__(attrs)

    def value_from_datadict(self, data, files, name):
        return tuple(data.get(name+suffix,None) for suffix in self.suffixes)

    def render(self, name, value, attrs=None, renderer=None):
        ## value puo' arrivare come tripletta o come datetime.date
        try:
            value = (value.hour,value.minute)
        except AttributeError:
            pass
        if not value:
            value = (12,0)
        final_attrs = self.build_attrs(attrs)
        html = ''
        final_attrs['name'] = name+self.suffixes[0]
        html += '\n<select%s>' % flatatt(final_attrs)
        html += '<option value="">hour</option>'
        for i in range(24):
            selected=''
            try:
                if int(value[0])==i:
                    selected=' selected'
            except ValueError:
                pass
            html += '<option%s>%d</option>' % (selected,i)
        final_attrs['name'] = name+self.suffixes[1]
        html += '</select><select%s>' % flatatt(final_attrs)
        html += '<option value="">min</option>'
        for i in range(0,60,5):
            selected=''
            try:
                if int(value[1])==i:
                    selected=' selected'
            except ValueError:
                pass
            if i<10:
                s="0%d" % i
            else:
                s="%d" % i
            html += '<option%s value="%d">%s</option>' % (
                selected, i, s)
        html+='</select>\n'
        return mark_safe(html)

class TimeInputField(Field):
    widget = TimeWidget

    def clean(self, value):
        try:
            return time(int(value[0]),int(value[1]))
        except ValueError:
            raise ValidationError('invalid time')

def formfield_for_dbfield(db_field):
#    print "db_field:", db_field.name, type(db_field)
    required = not db_field.blank
    if type(db_field) == ManyToManyField:
        Input = {
            Person: PersonsField,
            Keyword: KeywordsInputField,
            Link: LinksInputField,
            Tag: TagsInputField,
            }[db_field.remote_field.model]
        form_field = Input(required=required)
    elif type(db_field) == DateField:
        form_field = db_field.formfield()
        form_field.input_formats = ['%Y-%m-%d','%d.%m.%Y','%d.%m.%y','%d/%m/%Y','%d/%m']
        form_field.widget.attrs['class'] = 'date_picker'
        form_field.widget.attrs['size'] = 11
#        form_field = DateInputField(required=required) # old widget
    elif type(db_field) == TimeField:
        form_field = db_field.formfield()
        form_field.input_formats = ('%H:%M','%H.%M','%H:%M:%S')
        form_field.widget.attrs['size'] = 6
#        form_field = TimeInputField(required=required)
    elif db_field.name == 'paper_type':
        form_field = PaperTypeField(required=required)
    elif db_field.name == 'position':
        form_field = PositionField(required=required)
    else:
        form_field=db_field.formfield()
        if db_field.name in ['year']:
            size = 5
        elif db_field.name in ['pages', 'volume', 'number']:
            size = 20
        else:
            size = 50
        form_field.widget.attrs['size']=size
        form_field.widget.attrs['cols']=60

    return form_field

class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ['lastname', 'firstname', 'affiliation', 'position', 'email',
                   'home_page', 'arxiv_id', 'orcid_id', 'description']
    position = PositionField(required=False)

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        for field, size in list({
                'lastname': 50,
                'firstname': 50,
                'affiliation': 50,
                'email': 50,
                'home_page':50,
        }.items()):
            self.fields[field].widget.attrs['size'] = size

    def clean_arxiv_id(self):
        data = self.cleaned_data['arxiv_id']
        data = data.strip()
        data = strip_leading(data, 'http://arxiv.org/a/')
        data = strip_trailing(data, '.html')
        return data

    def clean_orcid_id(self):
        data = self.cleaned_data['orcid_id']
        data = data.strip()
        if data == '':
            return data

        data = strip_leading(data, 'https://')
        data = strip_leading(data, 'http://')
        data = strip_leading(data, 'orcid.org/')
        if len(data) == 19:
            if data[4::5] != '---':
                raise ValidationError('dash separators expected')
            data = ''.join([data[5*i:5*i+4] for i in range(4)])
        elif len(data) != 16:
            raise ValidationError('19 characters with 16 digits expected')
        total = 0
        for c in data[0:15]:
            try:
                total = (total + int(c)) * 2
            except ValueError:
                raise ValidationError('not a valid digit')

        check = (12 - (total % 11)) % 11
        check = str(check) if check<10 else 'X'
        if data[-1] != check:
            raise ValidationError('checksum error')
        data = '-'.join([data[4*i:4*i+4] for i in range(4)])
        return data


class PaperForm(ModelForm):
    class Meta:
        model = Paper
        fields = ['title', 'authors', 'paper_type', 'doi',
                  'arxiv_id', 'year', 'journal', 'pages', 'volume',
                  'number', 'keywords', 'links', 'notes', 'abstract', 'tags']

    authors = PersonsField()
    paper_type = PaperTypeField()
    keywords = KeywordsInputField(required=False)
    links = LinksInputField(required=False)
    tags = TagsInputField(required=False)

    def __init__(self, *args, **kwargs):
        super(PaperForm, self).__init__(*args, **kwargs)
        for field, size in list({
                'title': 60,
                'volume': 20,
                'number': 20,
                'year': 5,
                'journal': 50,
                'doi': 50,
                'title': 50,
        }.items()):
            self.fields[field].widget.attrs['size'] = size

    def clean_arxiv_id(self):
        patterns = [re.compile('arxiv:(.*)', re.IGNORECASE),
                    re.compile('https?://arxiv.org/abs/(.*)')]

        data = self.cleaned_data['arxiv_id']
        data = data.strip()
        for pattern in patterns:
            r = pattern.match(data)
            if r:
                data = r.groups()[0]
        return data

class MyDateFormField(forms.fields.DateField):
    input_formats = ['%Y-%m-%d','%d.%m.%Y','%d.%m.%y','%d/%m/%Y','%d/%m']

    def __init__(self, *args, **kwargs):
        super(MyDateFormField, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] = 'date_picker'
        self.widget.attrs['size'] = 11

class MyCharField(forms.fields.CharField):
    def __init__(self, *args, **kwargs):
        size = kwargs.pop('size', None)
        super(MyCharField, self).__init__(*args, **kwargs)
        if size is not None:
            self.widget.attrs['size'] = size

class MyTextField(forms.fields.CharField):
    widget = forms.widgets.Textarea
    def __init__(self, cols=50, **kwargs):
        super(MyTextField, self).__init__(**kwargs)
        self.widget.attrs['cols'] = cols

class MyIntegerField(forms.fields.IntegerField):
    pass

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title','description','hidden', 'date_from','date_to','crm_id', 'place','speakers','organizers','registration_page_enabled','registration_deadline','grant_application_enabled','grant_request_deadline','grant_description','links','keywords']

    title = MyCharField(size=50)
    description = MyTextField(required=False)

    crm_id = MyIntegerField(required=False)

    hidden = forms.fields.BooleanField(required=False)

    date_from = MyDateFormField()
    date_to = MyDateFormField()

    place = MyCharField(required=False)

    speakers = PersonsField(required=False)
    organizers = PersonsField(required=False)

    registration_page_enabled = forms.fields.BooleanField(required=False)
    registration_deadline = MyDateFormField(required=False)
    grant_application_enabled = forms.fields.BooleanField(required=False)
    grant_request_deadline = MyDateFormField(required=False)
    grant_description = MyTextField(required=False)

    links = LinksInputField(required=False)
    keywords = KeywordsInputField(required=False)

    def clean_crm_id(self):
        data = self.cleaned_data['crm_id'] or 0
        return data

def getModelForm(Model):
    if Model is Paper:
        return PaperForm
    elif Model is Person:
        return PersonForm
    elif Model is Event:
        return EventForm
    form = modelform_factory(
        Model,
        formfield_callback=formfield_for_dbfield,
        fields=Model.form_fields
        )
    return form

def saveRelatedFields(cleaned_data):
    for item in list(cleaned_data.values()):
        if type(item) == list:
            for obj in item:
                if not obj.pk:
                    obj.save()

def PaperOrderForm(Form):
    choices = (('year','year'),
               ('creation_time','insertion'),
               ('authors','authors'))

#class PersonRequestForm(getModelForm(PersonRequest)):
#    pass

class HumanField(CharField):
    def validate(self, value):
        super(HumanField, self).validate(value)
        if value.lower() != 'yes':
            raise ValidationError('to prevent machine generated requests, you must declare to be human')
        return value

class PersonRequestForm(ModelForm):
    class Meta:
        model = PersonRequest
        fields = ('lastname','firstname','affiliation','position','email','notes')
    human = HumanField(max_length=20,label='Are you a Human being?')


class EventRegistrationForm(ModelForm):
    class Meta:
        model = EventParticipant
        fields = ('email','lastname','firstname','affiliation','position','date_from','date_to','grant_state','notes')
        widgets = {
            'grant_state': Select,
            }

    def __init__(self, *args, **kwargs):
        kwargs = dict(kwargs) # make a copy
        initial = kwargs.pop('initial',{})
        person = kwargs.pop('person',None)
        event = kwargs.pop('event',None)

        if person:
            initial['lastname'] = person.lastname
            initial['firstname'] = person.firstname
            initial['email'] = person.email
            initial['affiliation'] = person.affiliation
            initial['position'] = person.position

        if event:
            initial['date_from'] = event.date_from
            initial['date_to'] = event.date_to

        kwargs['initial']=initial

        super(EventRegistrationForm,self).__init__(*args,**kwargs)

        self.fields['document'] = FileField(label='Curriculum (PDF)', required=False)

        self.fields['grant_state'].choices = [('no','no'),('requested','yes')]
        self.fields['grant_state'].label = 'Apply for a grant?'
        if event and not event.grant_request_is_open():
            self.fields.pop('grant_state')
        for field in ('date_to', 'date_from'):
            self.fields[field].widget.attrs['class']  = 'date_picker'
    def save(self,*args,**kwargs):
        obj = super(EventRegistrationForm,self).save(*args,**kwargs)

        recursive_save_m2m = None

        def save_m2m():
            if recursive_save_m2m is not None:
                recursive_save_m2m()
            file = self.cleaned_data['document']
            if file:
                document = Document(file=file,description='curriculum')
                document.upload_to = os.path.join('doc',obj.codename(),'%d' % obj.pk)
                document.save()
                obj.documents.add(document)

        if kwargs.get('commit',True):
            save_m2m()
        else:
            recursive_save_m2m = self.save_m2m
            self.save_m2m = save_m2m

        return obj

EventParticipantFormset = modelformset_factory(EventParticipant, exclude=[])

class CurriculumForm(Form):
    email = EmailField()
    file = FileField()

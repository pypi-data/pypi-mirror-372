import datetime
import os
import re
from collections import defaultdict, OrderedDict
from jinja2 import BaseLoader, TemplateNotFound
from functools import total_ordering

from django.contrib.sites.models import Site
from django.db.models.fields.files import ImageField
from django.core.mail import EmailMultiAlternatives
from jinja2 import BaseLoader

from django.db import models
from django.db.models import Model, CharField, TextField, ForeignKey, DateTimeField, BooleanField, EmailField, GenericIPAddressField, FileField, IntegerField, ManyToManyField, DateField, OneToOneField, URLField, TimeField, SlugField, Q
from django.db.models import Value
from django.db.models.functions import Concat
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str
from hashlib import md5, sha1
from django.template import TemplateDoesNotExist
from django.template.loaders.base import Loader as BaseLoader
from django.template.loader import get_template
from django.utils._os import safe_join
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.urls import reverse


from piprints.settings import ROOT_URL, SERVER_URL, FAKE_EMAILS
from piprints import settings
from .data_import import get_arxiv_abstract, ArxivError
from .templatetags.piprints import simpletags

from piprints.settings import SERVER_EMAIL

DATE_HELP_TEXT="yyyy-mm-dd"

def format_date(d):
    return d.strftime('%e %b %Y')

def format_date_interval(start,end):
    if start.year == end.year:
        if start.month == end.month:
            return '%d - %s' % (start.day,end.strftime('%e %b %Y'))
        return '%s - %s' % (start.strftime('%e %b'),end.strftime('%e %b %Y'))
    return '%s - %s' % (start.strftime('%e %b %Y'),end.strftime('%e %b %Y'))

class Log(Model):
    creation_time = DateTimeField(auto_now_add=True)
    username = CharField(max_length=80, blank=True, default='')
    action = CharField(max_length=1024, blank=True, default='')
    dump = TextField(blank=True, default='')

    # old model
    o_creation_time = DateTimeField(blank=True, null=True, default=None)
    def __str__(self):
        return '[%s] %s: %s' % (
            self.creation_time,
            self.username,
            self.action)

class BaseModel(Model):
    class Meta:
        abstract = True

    creation_time = DateTimeField(auto_now_add=True, null=True, editable=False)
    modification_time = DateTimeField(auto_now=True, null=True, editable=False)
    created_by = ForeignKey('User', blank=True, null=True,
                                   related_name='created_%(class)s',
                                   default=None, editable=False,
                            on_delete=models.SET_NULL)
    modified_by = ForeignKey('User', blank=True, null=True,
                                    related_name='modified_%(class)s',
                                    default=None, editable=False,
                             on_delete=models.SET_NULL)
    hidden = BooleanField(default=False)


    def is_new(self):
        return self.creation_time >= datetime.datetime.now() - datetime.timedelta(14)

    def is_updated(self):
        return (self.modification_time >=
                datetime.datetime.now() - datetime.timedelta(14) and
                self.creation_time < datetime.datetime.now() - datetime.timedelta(1))

    def attach_permissions(self,user):
        self.sendable = False
        self.editable = False
        self.deletable = False
        try:
            try:
                self.sendable = user.is_active and user.person and user.person.email
            except Person.DoesNotExist:
                pass
            self.editable = user.can_edit(self)
            self.deletable = user.can_delete(self)
        except AttributeError:
            pass # anonymous user
        return self

    def is_also_editable_by(self, user):
        return False

    def info_list(self):
        opts = type(self)._meta
        return [ {'field': field.name, 'value': getattr(self,field.name)}
                 for field in opts.fields] + [ {'field': field.name, 'value': getattr(self,field.name).all()} for field in opts.many_to_many]

    def codename(self):
        code = self._meta.verbose_name
        if code == 'open position':
            code = 'position'
        return code

    def html_admin_buttons(self):
        s=''
        codename = self.codename()
        # questi attributi vengono settati da attach_permissions. Facciamo in modo
        # che non dia errore se non ci sono...
        if getattr(self, 'editable', False):
            s+=' <a class="admin" href="'+ROOT_URL+'edit/%s/%d/">[edit]</a>' % (
                codename,self.pk)
            if codename == 'person' and self.user:
                s+=' <a class="admin" href="'+ROOT_URL+'passwd/%d/">[change password]</a>' % self.user.pk
        if hasattr(self,'deletable') and self.deletable:
            s+=' <a class="admin" href="'+ROOT_URL+'remove/%s/%d/">[delete]</a>' % (
                codename,self.pk)
        if hasattr(self,'sendable') and self.sendable and codename in ['news','event','seminar','position']:
            s+=' <a class="admin" href="'+ROOT_URL+'send/%s/%d/">[send by email]</a>' %(
                codename,self.pk)
        if isinstance(self,Person) and self.user is None:
            s+=' <a class="admin" href="%s">[view]</a>' % self.url()
        return mark_safe(s)

    def html_timestamps(self):
        DATE_FORMAT = '%0d %b %Y'
        s= ''
        s+='<div class="timestamps">created '
        try:
            s+="by %s " % self.created_by.username
        except AttributeError:
            pass
        if self.creation_time:
            s+="on %s " % self.creation_time.strftime(DATE_FORMAT)
        if self.modification_time and ((not self.creation_time) or  self.modification_time.date() != self.creation_time.date()):
            s+="<br>modified "
            if self.modified_by != self.created_by:
                try:
                    s+="by %s " % self.modified_by.username
                except AttributeError:
                    pass
            s+="on %s " % self.modification_time.strftime(DATE_FORMAT)
        s+="</div>\n"
        return mark_safe(s)

    def absolute_url(self):
        return SERVER_URL + self.url()

class MyUserManager(BaseUserManager):
    """
    need to rewrite of django.contrib.auth.models.UserManager
    because our Users don't have email field
    """

    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

class User(BaseModel, AbstractBaseUser):
    username = CharField(max_length=16, unique=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    objects = MyUserManager()

    form_fields = ['username','password','is_active','is_staff','is_superuser']

    USERNAME_FIELD = 'username' # required by django

    @property
    def person(self):
        if not hasattr(self,'_person_cached'):
            try:
                self._person_cached = Person.objects.get(user=self)
            except Person.DoesNotExist:
                self._person_cached = None
        return self._person_cached

    class Meta:
        ordering = ['username']

    @property
    def message_set(self):
        """
        Questa e' una patch!
        l'interfaccia di admin si aspetta questo manager.
        """
        from django.contrib.messages import get_messages as Message
        return Message.objects.none()

    def html(self):
        s = self.username
        if self.person:
            s += ' (%s %s)' % (self.person.firstname, self.person.lastname)
        return s

    def can_login(self):
        return self.is_active

    @property
    def is_authenticated(self):
        """ just to distinguish from the AnonymousUser """
        return True

    @property
    def is_anonymous(self):
        return False

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, permissions):
        print(('assume %s has permissions %s' % (self.username, permissions)))
        return True

    def get_and_delete_messages(self):
        return []

    def can_list(self, cls):
        if self.is_superuser or self.is_staff:
            return True

        if cls == User:
            return False

        if cls == Log:
            return False

        return True

    def can_create(self, cls):
        if self.is_superuser or self.is_staff:
            return True

        # normal user cannot manage other users
        if cls == User:
            return False

        # any authenticated user can add papers and news...
        return True

    def can_edit(self,obj):
        if self.is_staff or self.is_superuser:
            return True

        if obj.created_by == self:
            return True
        if obj.is_also_editable_by(self):
            return True

        return False

    def can_delete(self,obj):
        if type(obj) == Person:
            return False
        return self.can_edit(obj)

def document_upload_to(instance, filename): ## NON USATO?!?
    return os.path.join('doc',instance.upload_to,filename)

class Document(BaseModel):
    description = CharField(max_length=200)
    file = FileField(max_length=255,upload_to=document_upload_to)

    def url(self):
        return self.file.url

    def __str__(self):
        return '%s' % self.description

class Person(BaseModel):
    crm_id = IntegerField(blank=True,default=0)
    arxiv_id = CharField(max_length=250, blank=True)
    orcid_id = CharField(max_length=80, blank=True)
    user = OneToOneField(User,blank=True,null=True,related_name='_person',on_delete=models.SET_NULL)
    lastname = CharField(max_length=60)
    firstname = CharField(max_length=60)
    affiliation = CharField(max_length=250, blank=True)
    position = CharField(max_length=80, blank=True)
    email = EmailField(max_length=80, blank=True)
    home_page = URLField(max_length=250, blank=True)
    description = TextField(blank=True)

    # form_fields = ['lastname','firstname','affiliation','position','email',
    # 'home_page','description']

    class Meta:
        ordering=('lastname','firstname')

    def __str__(self):
        if self.user:
            return "%s %s (%s)" % (self.lastname,self.firstname,self.user.username)
        else:
            return "%s %s" % (self.lastname,self.firstname)

    def url(self):
        return ROOT_URL+'person/%d/' % self.pk

    def short(self):
        s = ''
        for c in self.firstname:
            if c.isupper():
                s += c+'. '
        s += self.lastname
        return s

    def html_short(self):
        s = self.short()
        if self.user:
            s = '<a class="person" href="%s">%s</a>' % (self.url(), s)
        return mark_safe(s)

    def html(self):
        s = '%s %s' % (self.firstname, self.lastname)
        if self.user:
            s = '<a href="%s">%s</a>' % (self.url(), s)
        l = [x for x in [self.position, self.affiliation] if x]
        if l:
            s+=' (%s)' % ", ".join(l)
        return mark_safe(s)

    def email_hidden(self):
        if '@' in self.email:
            return mark_safe(' <b>AT</b> '.join(self.email.split('@')))
        return None

    def is_also_editable_by(self, user):
        try:
            return user.person == self
        except Person.DoesNotExist:
            return False

class Keyword(Model):
    name = CharField(max_length=80,unique=True)

    def __str__(self):
        return self.name

    def url(self):
        return ROOT_URL+'keyword/%d/' % self.pk

class Link(Model):
    url = URLField(max_length=250)
    description = TextField()

def dup(lst):
    return [(x,x) for x in lst]

class Tag(Model):
    value = CharField(max_length=16, unique=True)

    def __str__(self):
        return self.value

    def url(self):
        return ROOT_URL+'papers/?tag=%d' % self.pk

    def html(self):
        return mark_safe('<a href="%s">%s</a>' % (self.url(),self))

@total_ordering
class Paper(BaseModel):
    # form_fields = ['title','authors','paper_type','doi','arxiv_id','year','journal','pages','volume',
    # 'number','keywords','links','notes','abstract','tags']

    class Meta:
        pass

    code = CharField(max_length=32, unique=True)
    title = CharField(max_length=250)
#    authors_old = ManyToManyField(Person,blank=True,related_name='papers')
    authors = ManyToManyField(Person, through='PaperAuthor', related_name='papers')
    paper_type = CharField(max_length=160,default='', blank=True)
    doi = CharField(max_length=280,default='', blank=True)
    arxiv_id = CharField(max_length=1024, blank=True) #, help_text="arxiv.org abstract identifier e.g. math/0611800")
    year = IntegerField(db_index=True,null=False)
    journal = CharField(max_length=250,blank=True)
    volume = CharField(max_length=32,blank=True)
    number = CharField(max_length=32,blank=True)
    pages = CharField(max_length=20,blank=True)
    notes = TextField(blank=True)
    keywords = ManyToManyField(Keyword,blank=True)
    links = ManyToManyField(Link,blank=True)
    abstract = TextField(blank=True)
    documents = ManyToManyField(Document,blank=True)
    notification_sent = BooleanField(default=False)
    tags = ManyToManyField(Tag,blank=True)

    def ordered_authors(self):
        return [x.person for x in PaperAuthor.objects.filter(
                paper=self).order_by('order')]

    def __str__(self):
        return "%s (%s)" % (self.title, " - ".join([str(a) for a in self.authors.all()]))

    def txt(self):
        s = '%s:\n' % ", ".join(a.short() for a in self.authors.all())
        s += '%s\n' % self.title
        if self.journal:
            s+= '%s ' % self.journal
        if self.paper_type not in ('Published Paper',):
            s+= '(%s) ' % self.paper_type
            if self.arxiv_id:
                s+= self.arxiv_url() + ' '
        lst = []
        if self.volume:
            lst.append('Vol. %s' % self.volume)
        if self.number:
            lst.append('N. %s' % self.number)
        if self.pages:
            lst.append('p. %s' % self.pages)
        if self.year:
            lst.append('%s' % self.year)
        s+=', '.join(lst)+'\n'

        return s

    def url(self):
        return ROOT_URL+'paper/%d/' % self.pk

    def arxiv_url(self):
        if not self.arxiv_id: return None
        return 'http://arxiv.org/abs/%s' % self.arxiv_id

    def arxiv_pdf_url(self):
        if not self.arxiv_id: return None
        return 'http://arxiv.org/pdf/%s' % self.arxiv_id

    def get_absolute_url(self):
        return reverse('paper', args=[self.id])

    def html(self):
        s = ''
        s += " - ".join([x.html_short() for x in self.ordered_authors()])
        t = None
        if self.paper_type != 'Published Paper':
            t = self.paper_type
        if t or self.journal:
            if t and self.journal:
                s+=' (%s: <i>%s</i>)' % (t, self.journal)
            elif self.journal:
                s+=' (<i>%s</i>)' % self.journal
            else:
                s+=' (%s)' % t
        s+='<br>'
        s+='<a class="paper" href="%s">%s</a>' % (self.url(),self.title)
        ## TODO: mettere icone PDF e PS
        if self.year:
            s+=' (%s)' % self.year
        return mark_safe(s)

    def sort_tuple(self):
        if not hasattr(self,'_sort_tuple_cache'):
            self._sort_tuple_cache=(tuple([ x.lastname+' '+x.firstname for x in self.authors.all()]),self.year,self.title)
        return self._sort_tuple_cache

    def is_also_editable_by(self, user):
        try:
            return user.person in self.authors.all()
        except Person.DoesNotExist:
            return False

    def __lt__(self,other):
        return self.sort_tuple() < other.sort_tuple()
    
    def __eq__(self,other):
        return self.sort_tuple() == other.sort_tuple()
    
    def __ne__(self,other):
        return self.sort_tuple() != other.sort_tuple()

    def __hash__(self):
        return "Paper".__hash__() ^ super().__hash__()

    # def clean(self):
    #     print 'custom cleaning of Paper %s' % self.title
    #     if not self.code:
    #         self.code = self.get_unique_code(self.authors, self.year)
    #         print 'assigned code: %s' % self.code
    #     return super(Paper,self).clean()

    def get_unique_code(self, authors, year):
        n = 3
        if len(authors)>5:
            n = 1
        elif len(authors)>3:
            n = 2
        code = ''.join([x.lastname.replace(' ','')[:n] for x in authors])+str(year%100)
        basecode = code
        mod = 0
        while Paper.objects.filter(code=code):
            code = basecode+''.join("abcdefghil"[ord(x)-ord('0')]
                                    for x in str(mod))
            mod += 1
        return code

    def first_page(self):
        return self.pages.split('-')[0]

    def last_page(self):
        return self.pages.split('-')[-1]

    def update_from_arxiv(self, save=True):
        d = get_arxiv_abstract(self.arxiv_id)
        self.title = d.get('title', self.title)
        self.abstract = d.get('summary', self.abstract)
        if not self.year:
            self.year = str(d['published'].year)
        authors = []
        for author in d['authors']:
            try:
                authors.append(
                    Person.objects.annotate(name=Concat('firstname', Value(' '), 'lastname')
                                        ).get(name=author))
            except Person.DoesNotExist:
                names = author.split(' ')
                if len(names) == 2:
                    authors.append(Person(lastname=names[1], firstname=names[0]))
                else:
                    authors.append(Person(lastname=author, firstname=''))
            except Person.MultipleObjectsReturned:
                raise ArxivError("multiple Person for {}".format(author))
        if not self.code:
            self.code = self.get_unique_code(authors, int(self.year))
        def update_m2m_helper():
            PaperAuthor.objects.filter(paper=self).delete()
            for (i, person) in enumerate(authors):
                if not person.id:
                    person.save()
                PaperAuthor(paper=self, person=person, order=i).save()
        if save:
            self.save()
            update_m2m_helper()
        else:
            return update_m2m_helper

    def feed_description(self):
        authors = ', '.join(author.short() for author in self.authors.all())
        return '{}.\n{}\n{}'.format(authors, simpletags(self.abstract), simpletags(self.notes))


class PaperAuthor(BaseModel):
    paper = ForeignKey(Paper, on_delete=models.CASCADE)  # togli l'autore quando il paper viene cancellato
    person = ForeignKey(Person, on_delete=models.PROTECT)
    order = IntegerField()

    class Meta:
        ordering = ('order', )

    def __str__(self):
        return "PaperAuthor({person.lastname},{paper.title})".format(person=self.person, paper=self.paper)

class News(BaseModel):
    title = CharField(max_length=250)
    description = TextField(blank=True)
    links = ManyToManyField(Link, blank=True)
    keywords = ManyToManyField(Keyword,blank=True)
    documents = ManyToManyField(Document,blank=True)

    form_fields = ['title','links','keywords','description']

    class Meta:
        verbose_name_plural = 'News'

    def url(self):
        return ROOT_URL+"news/%d/" % self.pk

    def get_absolute_url(self):
        return reverse('news', args=[self.id])

    def __str__(self):
        return self.title

    def html(self):
        return mark_safe('%s: <a href="%s">%s</a>' % (
                format_date(self.creation_time),
                self.url(),
                self.title or '???'))

    def feed_description(self):
        return '{}'.format(simpletags(self.description))


class TimesheetWeek(object):
    """
    oggetto che rappresenta una settimana di timesheet
    """
    def __init__(self):
        self.days = defaultdict(list)

    def add(self,seminar):
        self.days[seminar.date].append(seminar)

    def items(self):
        items = sorted(list(self.days.items()), key = (lambda x: x[0]))
        return items

    def __iter__(self):
        for key in sorted(self.days.keys()):
            yield key

class Timesheet(object):
    """
    oggetto che rappresenta la timesheet di un Event
    """
    def __init__(self,event):
        self.event = event
        self.seminars = Seminar.objects.filter(parent=self.event,date_is_valid=True,time__isnull=False)

    def weeks(self):
        def week_num(timestamp):
            return timestamp.date().toordinal() // 7
        weeks = defaultdict(list)
        for seminar in self.seminars:
            weeks[week_num(datetime.datetime.combine(seminar.date,seminar.time))].append(seminar)
        for k in sorted(weeks.keys()):
            week = TimesheetWeek()
            for seminar in sorted(weeks[k],key=lambda x: (x.date,x.time)):
                week.add(seminar)
            yield week

class CalendarModel(BaseModel):
    class Meta:
        abstract = True

    google_id = CharField(max_length=30, blank=True, null=False, default='', help_text="id of event in google calendar")

    def google_event_dict(self):
        """
        override to return a google calendar event dict as described in
        https://developers.google.com/google-apps/calendar/v3/reference/events/insert
        if None is returned the event is not stored in the calendar
        """
        return None

    def google_calendar_save(self, api=None):
        if api is None:
            api = get_google_api(require_calendar=True)
        if not api:
            return
        event = self.google_event_dict()
        if not event:
            return
        if self.google_id:
            api.calendar_update_event(self.google_id, event)
        else:
            self.google_id = api.calendar_add_event(event)
            super(CalendarModel, self).save(update_fields=['google_id'])

    def save(self, *args, **kwargs):
        update_calendar = kwargs.pop('update_calendar', True)
        r = super(CalendarModel, self).save(*args, **kwargs)
        if update_calendar:
            self.google_calendar_save()
        return r

    def delete(self, *args, **kwargs):
        if self.google_id:
            api = get_google_api(require_calendar=True)
            if api:
                api.calendar_delete_event(self.google_id)
        return super(CalendarModel, self).delete(*args, **kwargs)

class Event(CalendarModel):
    crm_id = IntegerField(blank=True, default=0)
    title = CharField(max_length=250)
    slug = SlugField(max_length=32, blank=True, default='', help_text="if provided the event will be accessible with the URL <i>/slug</i>")
    parent = ForeignKey('Event', blank=True, null=True,
                               related_name='sub_events', on_delete=models.PROTECT)
    date_from = DateField(help_text="first day of event")
    date_to = DateField("last day of event")
    place = CharField(max_length=80, blank=True)
    description = TextField(blank=True)
    speakers = ManyToManyField(Person,blank=True,related_name='invited_events')
    organizers = ManyToManyField(Person,blank=True,related_name='organized_events')
    links = ManyToManyField(Link, blank=True)
    keywords = ManyToManyField(Keyword, blank=True)
    documents = ManyToManyField(Document,blank=True)

    #form_fields = ['title','description','date_from','date_to','place','speakers','organizers','registration_page_enabled','registration_deadline','grant_application_enabled','grant_request_deadline','grant_description','links','keywords']

    registration_deadline = DateField(null=True,blank=True, help_text="last day for registration")
    grant_request_deadline = DateField(null=True,blank=True, help_text="last day for requesting a grant")
    registration_page_enabled = BooleanField(default=False, help_text="if checked a registration page will be generated")
    grant_application_enabled = BooleanField(default=False, help_text="if checked grant request will be enabled")

    grant_description = TextField(blank=True, help_text="write here any comments regarding the grant")

    timetable_enabled = BooleanField(default=False, help_text="if checked a timetable will be generated")

    class Meta:
        ordering = ['-date_from','title']

    def has_not_confirmed_seminars(self):
        return bool(Seminar.objects.filter(parent=self,hidden=False,to_be_confirmed=True))

    def expired(self):
        return date_to > datetime.datetime.now()

    def is_new(self):
        return BaseModel.is_new(self) and not self.expired()

    def is_updated(self):
        return BaseModel.is_updated(self) and not self.expired()

    def url(self):
        return ROOT_URL+"event/%d/" % self.pk

    def get_absolute_url(self):
        return reverse('event', args=[self.id])

    def __str__(self):
        return self.title

    def html(self):
        return mark_safe('%s: <a href="%s">%s</a> %s' %
                         (format_date_interval(self.date_from,self.date_to),
                          self.url(), self.title,self.place))

    def is_also_editable_by(self, user):
        try:
            return user.person in self.organizers.all()
        except Person.DoesNotExist:
            return False

    def registration_is_open(self):
        if not self.registration_page_enabled:
            return False
        registration_deadline = self.registration_deadline or self.date_to
        if registration_deadline and datetime.date.today() > registration_deadline:
            return False
        return True

    def grant_request_is_open(self):
        if self.grant_request_deadline and datetime.date.today() > self.grant_request_deadline:
            return False
        return self.grant_application_enabled

    def confirmed_participants(self):
        return EventParticipant.objects.filter(event=self,state='accepted').order_by('lastname','firstname')

    def pending_registrations(self):
        return EventParticipant.objects.filter(event=self).filter(Q(state='requested') | Q(grant_state='requested')).order_by('lastname','firstname')

    def timesheet(self):
        return Timesheet(self)

    def google_event_dict(self):
        return dict(
            summary=self.title,
            description="""{self.description}
            {url}
            """.format(self=self,url=self.absolute_url()),
            start=dict(date=self.date_from.isoformat()),
            end=dict(date=max(self.date_to+datetime.timedelta(days=1), self.date_from).isoformat()),
            location=self.place,
            source=dict(title='piprints', url=self.absolute_url())
        )

    def feed_description(self):
        return '{}: {}. \n{}'.format(
            format_date_interval(self.date_from, self.date_to),
            self.place,
            simpletags(self.description)
        )


class Seminar(CalendarModel):
    crm_id = IntegerField(blank=True, default=0)
    title = CharField(max_length=250)
    parent = ForeignKey('Event', blank=True, null=True,
                               related_name='seminars', help_text="the seminar is part of an event? Choose here the event.",
                               on_delete=models.PROTECT)
    type = CharField(max_length=30, choices=[(x,x) for x in ['seminar','course','separator']], default='seminar')
    speakers = ManyToManyField(Person,related_name='seminars',blank=True)
    date = DateField(help_text=DATE_HELP_TEXT)
    date_is_valid = BooleanField(default=True, help_text="uncheck this if the date is not confirmed.")
    time = TimeField(blank=True,null=True)
    place = CharField(max_length=80,blank=True)
    description = TextField(blank=True)
    abstract = TextField(blank=True)
    links = ManyToManyField(Link, blank=True)
    keywords = ManyToManyField(Keyword, blank=True)
    documents = ManyToManyField(Document,blank=True)
    to_be_confirmed = BooleanField(default=False, help_text="check this if the seminar hasn't been confirmed.")

    form_fields = ['title','date','time','date_is_valid','place','speakers','to_be_confirmed','links','keywords','abstract','description']

    def __str__(self):
        return self.title

    def url(self):
        return ROOT_URL+"seminar/%d/" % self.pk

    def get_absolute_url(self):
        return reverse('seminar', args=[self.id])

    def html(self):
        if self.date_is_valid:
            s='%s: ' % format_date(self.date)
        else:
            s=''
        return mark_safe(s+'<b>%s%s:</b> <i><a href="%s">%s</a></i>' % (
                ', '.join([x.html_short() for x in self.speakers.all()]),
                {True: '(*)', False: ''}[self.to_be_confirmed],
                self.url(),
                self.title)
                + {True: ' ' + self.place, False: ''}[settings.SHOW_SEMINAR_PLACE])

    def is_also_editable_by(self, user):
        try:
            person = user.person
        except Person.DoesNotExist:
            return False
        if person in self.speakers.all():
            return True
        if self.parent and user.can_edit(self.parent): # organizer of the parent event?
            return True
        return False

    def google_event_dict(self):
        if not self.time:
            return None
        start = datetime.datetime.combine(self.date, self.time)
        summary = "{}".format(self.title)
        description="""{self.description}
{self.abstract}
{url}""".format(self=self,url=self.absolute_url())
        try:
            speaker = self.speakers.all()[0]
            summary = "{}: {}".format(speaker.lastname, summary)
            description = "{}: {}".format(speaker.lastname, description)
        except IndexError:
            pass
        return dict(
            summary=summary,
            description=description,
            start=dict(dateTime=start.isoformat(), timeZone="Europe/Rome"),
            end=dict(dateTime=(start+datetime.timedelta(hours=1)).isoformat(), timeZone="Europe/Rome"),
            location=self.place,
            source=dict(title='piprints', url=self.absolute_url()))

    def feed_description(self):
        return '{}: {}.\n{}\n{}'.format(
            self.date,
            ', '.join([x.html_short() for x in self.speakers.all()]),
            simpletags(self.description),
            simpletags(self.abstract))


# open positions
class Position(BaseModel):
    class Meta:
        verbose_name='open position'

    title = CharField(max_length=250)
    description = TextField(blank=True)
    links = ManyToManyField(Link, blank=True)
    deadline = DateField()
    documents = ManyToManyField(Document,blank=True)

    form_fields = ['title','deadline','links','description']

    def url(self):
        return ROOT_URL+"position/%d/" % self.pk

    def get_absolute_url(self):
        return reverse('position', args=[self.id])

    def __str__(self):
        return self.title

    def html(self):
        return mark_safe('<a href="%s">%s</a> (deadline: %s)' % (
                self.url(), self.title, format_date(self.deadline)))

    def feed_description(self):
        return '{}: {}'.format(
            format_date(self.deadline),
            simpletags(self.description))

class PersonRequest(BaseModel):
    lastname = CharField(max_length=60)
    firstname = CharField(max_length=60)
    affiliation = CharField(max_length=250, blank=True)
    position = CharField(max_length=80, blank=True)
    email = EmailField(max_length=80)
    notes = TextField(blank=True)
    managed = BooleanField(default=False)
    ip = GenericIPAddressField(blank=True, default=None, null=True)

    form_fields = ['lastname','firstname','affiliation','position','email',
                   'notes']

    def __str__(self):
        return '%s request from %s %s' % ('managed' if self.managed else 'pending', self.lastname, self.firstname)

    class Meta:
        ordering = ('-creation_time',)

    def url(self):
        return ROOT_URL + 'personRequest/%d/' % self.pk

    def str(self):
        return "%s %s" % (self.firstname, self.lastname)

    def html(self):
        html = '<a href="'+ROOT_URL+'person_request/%d/">%s %s</a>' % (
            self.pk, self.firstname, self.lastname)
        return mark_safe(html)

class Template(BaseModel):
#    PAGE_CHOICES = dup(('self','base','Event','Seminar','registration'))

    name = CharField(max_length=250, blank=False)
#    cls = CharField(max_length=16, choices=PAGE_CHOICES, default='self')
    source = TextField(blank=True)

    event = ForeignKey(Event,null=True,on_delete=models.PROTECT)

    _cache = {} # id -> (timestamp,DjangoTemplate)

    class Meta:
        unique_together = ('event','name')

    def __str__(self):
        return 'template %s for event %s' % (self.name,self.event)

    def Template(self):
        from django.template import Template as DjangoTemplate
        if not (self.id in self._cache and self._cache[self.id][0] == self.modification_time):
            self._cache[self.id] = (self.modification_time,DjangoTemplate(self.template))
        return self._cache[self.id][1]

    def render(self,context):
        return self.Template().render(context)

class TemplateLoader(BaseLoader):
    is_usable = True
    event_re = re.compile(r'/event/(\d*)/(.*)')

    def load_template_source(self, template_name, template_dirs=None):
        m = self.event_re.match(template_name)
        if not m:
            raise TemplateDoesNotExist(template_name)
        event_id = int(m.group(1))
        name = m.group(2)
        try:
            return (Template.objects.get(event__id=event_id,cls=name).template,template_name)
        except Template.DoesNotExist:
            raise TemplateDoesNotExist(template_name)

    load_template_source.is_usable = True

class EventParticipant(BaseModel):
    STATE_CHOICES = dup(('requested','accepted','cancelled'))
    state = CharField(max_length=16, choices=STATE_CHOICES,default='requested')
    email = EmailField(max_length=80)
    email_verified = BooleanField(default=False) # not yet used
    verification_code = CharField(max_length=60,blank=True) # not yet used
    lastname = CharField(max_length=60)
    firstname = CharField(max_length=60)
    affiliation = CharField(max_length=250, blank=True)
    position = CharField(max_length=80, blank=True)
    event = ForeignKey(Event, on_delete=models.PROTECT)
    date_from = DateField()
    date_to = DateField()
    GRANT_STATE_CHOICES = dup(('no','requested','rejected','granted'))
    grant_state = CharField(max_length=16, choices=GRANT_STATE_CHOICES, default='no')
    notes = TextField(blank=True, default='')
    person = ForeignKey(Person,null=True,blank=True, on_delete=models.PROTECT)
    documents = ManyToManyField(Document,blank=True)

    form_fields = ['email','lastname','firstname','affiliation','position','date_from','date_to'] ## NON USATO?

    def __str__(self):
        return '%s %s' % (self.lastname,self.firstname)

class EmailMessage():
    """
    Messaggi email con possibilita' di rendere il testo da un template
    classe wrapper, eredita inizializzazione di mailer.Message:
    __init__(self, To=None, From=None, Subject=None, Body=None, Html=None, attachments=None, charset=None)

    attenzione: forse usa i template di django, non jinja2. Da verificare.
    """

    def __init__(self, to=None, subject=None, body=None, from_email=SERVER_EMAIL):
        if (isinstance(to, str)):
            to = [to]
        self.to = to or None
        self.subject = subject or None
        self.text_content = body or None
        self.html_content = None
        self.from_email=from_email

    def send(self, mailer=None):
        """
        sends message
        """
        if FAKE_EMAILS:
            print("FAKE EMAIL SENDING...")
            for attr in ['to', 'from_email', 'subject', 'text_content']:
                print(attr+": ", getattr(self, attr))
            return True
        msg = EmailMultiAlternatives(
            self.subject,
            self.text_content,
            self.from_email,
            self.to,
#            headers={"List-Unsubscribe": "<mailto:unsub@example.com>"},
        )
        
        if self.html_content:
            msg.attach_alternative(self.html_content, "text/html")

        return msg.send()

    def render_template(self,template_name,context=None):
        """
        renders the given django template with optional given context
        if the rendered text starts with a "Subject: " line sets the message.Subject
        then sets the message.Body with the rest of the rendered template
        """
        if context is None:
            context = {}
        template = get_template(template_name)
        body = template.render(context)
        body = body.splitlines()
        if body[0].startswith('Subject: '):
            self.subject = body[0][9:]
            body=body[1:]
            if not body[0]:
                body=body[1:]
        body = '\n'.join(body)
        self.text_content = body #.encode('utf-8')

    def render_html(self,template_name,context=None):
        """
        renders the given django template with optional given context
        and sets the message.Html part with rendered template
        """
        if context is None:
            context = {}
        template = get_template(template_name)
        self.html_content = template.render(context) #.encode('utf8')

    def get_args(self):
        """
        Returns a dictionary which describeds the email, suitable to
        be passed to log().
        """
        return {
            'subject': self.subject,
            'body': self.text_content,
            'from_email': self.from_email,
            'to': self.to,
            }


class ResearchProject(BaseModel):
    title = CharField(max_length=250, blank=False)
    principal_investigator = CharField(max_length=80, blank=True)
    external_url = URLField(blank=True)
    tag = CharField(max_length=80, blank=True)
    hide = BooleanField(default=False)  # questo andrebbe tolto: e' ridonante visto che BaseModel ha gia' l'attributo 'hidden'
    order = IntegerField(default=0)

    def __str__(self):
        return self.title


class SiteParameters(Site):
    site = OneToOneField(Site, on_delete=models.PROTECT, parent_link=True)
    title_banner = ImageField(blank=True)
    title = CharField(max_length=250, blank=True)
    welcome_message = TextField(blank=True)
    credits = TextField(blank=True)
    authorByContributionCount = IntegerField(default=20, help_text="number of people to be listed in the 'authors by contribution' page")
    google_service_account_credentials_json = TextField(blank=True, null=False, default='', help_text="copy the json content of a google service account credentials")
    google_calendar_id = CharField(max_length=1024, blank=True, null=False, default='', help_text="set this if you have a google calendar associated with a service account")
    google_custom_search_id = CharField(max_length=256, blank=True, null=False, default='', help_text="set this if you want a google custom search box")
    facebook_app_id = CharField(max_length=1024, blank=True, null=False, default='', help_text="set this if you have a facebook app id for the server")
    header_injection = TextField(blank=True, help_text="html code which will be inserted in every page at the end of the <head> section. Pay attention: insecure code might disrupt the server funcionality.")
    footer_injection = TextField(blank=True, help_text="html code which will be inserted in every page at the end of the <body> section. Pay attention: insecure code might disrupt the server funcionality.")

    class Meta:
        verbose_name_plural = 'site parameters'

    def save(self, *args, **kwargs):
        r = super(SiteParameters, self).save(*args, **kwargs)
        Site.objects.clear_cache()
        return r

    def get_google_api(self, require_calendar=False):
        if not self.google_service_account_credentials_json:
            return None
        if require_calendar and not self.google_calendar_id:
            return None
        from .google import GoogleApi
        return GoogleApi(self.google_service_account_credentials_json, calendar_id=self.google_calendar_id)

def get_google_api(*args, **kwargs):
    site = SiteParameters.objects.get(id=settings.SITE_ID)
    return site.get_google_api(*args, **kwargs)

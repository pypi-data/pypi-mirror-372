# -*- coding: utf-8 -*-

from functools import wraps, WRAPPER_ASSIGNMENTS
from urllib.parse import quote
import string
import unicodedata
#from unidecode import unidecode

#from django.utils.decorators import available_attrs
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse, JsonResponse
from django import forms
from django.template.loader import render_to_string
from django.shortcuts import render
from django.core import serializers
import json,csv
from django.contrib.messages import add_message, get_messages, ERROR, INFO, WARNING, SUCCESS
from django.conf import settings
from django.utils import timezone

from piprints.main.models import *
from piprints.main.forms import getModelForm, model_to_dict, saveRelatedFields, EventRegistrationForm, PersonRequestForm
from piprints.settings import MEDIA_ROOT, ROOT_URL, SERVER_EMAIL, BULLETIN_EMAIL, LIST_AUTHORS_BY_PAPERS, SITE_NAME, SERVER_URL, USE_PERSONAL_EMAIL, PERSONAL_EMAIL_TEMPLATE
from .template import dynamic_template_response
#from piprints.config import config

from .data_import import ArxivError, update_crm_event

class Redirect(Exception):
    def __init__(self,url):
        self.url = url


class NotAuthorized(Exception):
    pass


class NotFound(Exception):
    pass


class InvalidRequest(Exception):
    pass


def get_recursive_attr(obj, attr):
    for a in attr.split('__'):
        obj = getattr(obj, a)
    return obj


class CsvResponse(HttpResponse):
    def __init__(self, data, fields=None):
        super(CsvResponse, self).__init__(content_type='text/csv')
        self.fields = fields
        self.csv = csv.writer(self)
        self.write_content(data)

    def write_content(self, data):
        if self.content:
            return
        if hasattr(data, 'model'):
            # queryset?
            if self.fields is None:
                self.fields = [field.name for field in data.model._meta.fields]
        else:
            if self.fields is None:
                model = type(data[0])
                if hasattr(model, '_meta'):
                    self.fields = [field.name for field in model._meta.fields]
                assert self.fields
        self.csv.writerow(self.fields)

        def encode(item):
            if hasattr(item, 'encode'):
                return item.encode('utf-8')
            return item

        for item in data:
            self.csv.writerow([encode(get_recursive_attr(item, field)) for field in self.fields])

def page_not_found_view(request, exception):
    c = default_context_for(request)
    c['root_url'] = ROOT_URL
    return HttpResponseNotFound(render_to_string('404.html', c))

def catcher(view_func):
    """
    Decorator that catches some exceptions:
    Redirect: redirect to given URL
    """
    def wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except InvalidRequest:
            add_message(request, ERROR, 'Invalid request')
            return HttpResponseRedirect(ROOT_URL)
        except NotAuthorized:
            add_message(request, ERROR, 'Not Authorized')
            return HttpResponseRedirect(ROOT_URL)
        except Redirect as e:
            return HttpResponseRedirect(e.url)
        except NotFound as e:
            return page_not_found_view(request, e)
#        except ArxivError as e:
#            log(request.user, "arxiv error", ['{}'.format(e)])
#            add_message(request, ERROR, 'Arxiv error: {}'.format(e))
#            return HttpResponseRedirect(request.path)
    return wraps(view_func, assigned=WRAPPER_ASSIGNMENTS)(wrapped_view)


def check_authenticated_user(request):
    if not (request.user and request.user.is_authenticated):
        add_message(request, ERROR, 'authentication needed')
        raise Redirect(ROOT_URL + 'login/?next={}'.format(quote(request.path)))


def int_or_none(n):
    try:
        return int(n)
    except ValueError:
        return None
    except TypeError:
        return None


def html_admin_buttons(request,cls):
        s = ''
        codename = cls().codename()
        user = request.user
        if user.is_authenticated and user.can_create(cls):
            query = ''
            if cls == Paper and 'tag' in request.GET:
                query = '?tag=%s' % request.GET['tag']
            s += ' <a class="admin" href="'+ROOT_URL+'add/%s/%s">[add new %s]</a>' % (codename,query,codename)
        return mark_safe(s)


def default_context_for(request, cls=None):
    c = {}
    c['request'] = request
    if request:
        c['query_string'] = request.META['QUERY_STRING']
    if cls:
        c['html_admin_buttons'] = html_admin_buttons(request, cls)
    c['year'] = int_or_none(request.GET.get('year', None))
    if c['year'] is not None and c['year'] <= 0: c['year'] = None
    c['root_url'] = ROOT_URL
    c['settings'] = settings
    site = Site.objects.get_current()
    try:
        c['site'] = site.siteparameters
    except SiteParameters.DoesNotExist:
        c['site'] = SiteParameters(site=site)
    if request.user.is_authenticated:
        c['user'] = request.user
        if request.user.is_staff:
            c['person_requests'] = len(PersonRequest.objects.filter(managed=False))
    c['messages'] = get_messages(request)

    return c


def log(user, action, obj=None):
    l = Log()
    if user:
        l.username = user.username
    l.action = action
    if obj:
        try:
            # django ORM serializer
            l.dump = serializers.serialize('json',obj)
        except (AttributeError, TypeError):
            # simple serializer
            l.dump = json.dumps(obj)
    l.save()


def send_note_to_staff(request, person_request):
    requests = PersonRequest.objects.filter(managed=False).exclude(id=person_request.id)
    staff = Person.objects.filter(user__is_staff=True)

    c = default_context_for(request)
    to = [person.email for person in staff]
    c['to'] = to
    c['requests'] = requests
    c['person_request'] = person_request
    message = EmailMessage(to=to)
    message.render_template('mail/note_to_staff.mail', c)
    message.send()
    log(None, 'send email note to staff', message.get_args())


def send_new_password(user, request, welcome=False):
    import random

    c = default_context_for(request)
    to = user.person.email.split(',')
    c['user'] = user
    for logging in [False, True]:
        if logging:  # hide password in log message
            password = '<not shown>'
        else:
            password = ''.join([chr(ord('a')+random.randrange(0, 26)) for i in range(6)])
            user.set_password(password)
            user.save()
        c['password'] = password
        message = EmailMessage(to=to)
        if welcome:
            message.render_template('mail/password_new_user.mail', c)
        else:
            message.render_template('mail/change_password.mail', c)
        if logging:
            log(user, 'sent email password', message.get_args())
        else:
            message.send()

@catcher
def main_page(request):
    c = default_context_for(request)
    now = datetime.date.today()
    user = request.user
    for cls in [News, Position, Seminar, Event, Paper]:
        c['%s_html_admin_buttons' % cls().codename()] = html_admin_buttons(request,cls)
    c['last_added_papers']=[x.attach_permissions(user) for x in
                            Paper.objects.filter(
        hidden=False,
        creation_time__gt=now-datetime.timedelta(14)
        ).order_by('-creation_time')]
    c['last_modified_papers']=[
        x.attach_permissions(user) for x in
        Paper.objects.filter(
            hidden=False,
            modification_time__gt=now-datetime.timedelta(14))
        .order_by('-modification_time')
        if x not in c['last_added_papers']]
    c['news'] = [x.attach_permissions(user) for x in News.objects.filter(
        hidden=False, 
        creation_time__gt=now - datetime.timedelta(7))]
    seminars_filters = {}
    if not settings.SHOW_PARENTED_SEMINARS:
        seminars_filters['parent__isnull'] = True
    c['seminars'] = [x.attach_permissions(user) for x in Seminar.objects.filter(
        hidden=False, 
        date__gte=now, 
        date_is_valid=True, 
        type__in=['seminar', 'course'],
        **seminars_filters).order_by('date','time')]
    c['events'] = [x.attach_permissions(user) for x in Event.objects.filter(
        hidden=False,
        date_to__gte=now).order_by('date_from')]
    c['positions'] = [x.attach_permissions(user) for x in Position.objects.filter(
        hidden=False,
        deadline__gte=now).order_by('deadline')]
    c['projects'] = ResearchProject.objects.filter(
        hide=False, 
        hidden=False).order_by('order', 'title')
    return render(request, 'main.html', c)


## PAGINE CON ELENCHI

@catcher
def papers_page(request):
    c = default_context_for(request,Paper)
    template = 'papers.html'
    tag = request.GET.get('tag')
    if tag:
        try:
            try:
                tag = int(tag)
                tag = Tag.objects.get(pk=tag)
            except (ValueError,TypeError):
                tag = Tag.objects.get(value__iexact=tag)
        except Tag.DoesNotExist:
            raise NotFound()

        c['tag'] = tag
        papers = Paper.objects.filter(tags = tag)
        if 'erc' in request.GET:
            papers = list(papers.order_by('paper_type', 'year'))
            papers.sort(key=lambda x: (x.paper_type, x.year, x.sort_tuple()))
            template = 'papers_erc.html'
        else:
            papers = list(papers)
            papers.sort(key=lambda x: x.sort_tuple())
    else:
        c['years'] = Paper.objects.values_list('year', flat=True).order_by('-year').distinct()

        if c['year']:
            papers = list(Paper.objects.filter(year=c['year']))
            papers.sort(key=lambda x: x.sort_tuple())
        else:
            papers = Paper.objects.order_by('-creation_time')[:20]
    if 'txt' in request.GET:
        s = '\n'.join([paper.txt()
                       for paper in papers])
        return HttpResponse(s.encode('latin1','ignore'), content_type='text/plain')
    papers = [x.attach_permissions(request.user) for x in papers]
    if  'json' in request.GET:
        # for paper in papers:
            # paper.author_data = "ciccio"
            # [person for person in paper.authors.all()]
        data = serializers.serialize('json', papers, fields=('title', 'author_data'))
        return HttpResponse(data, content_type='application/json')
    c['papers'] = papers
    return render(request,template,c)

@catcher
def persons_page(request):
    c = default_context_for(request)
    site = c['site']
    initial = request.GET.get('letter', None)
    c['initial'] = initial
    c['initials'] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    persons = Person.objects.filter(hidden=False)

    if initial:
        persons = persons.filter(lastname__startswith=initial).order_by('lastname','firstname')
        if not (request.user.is_staff or request.user.is_superuser):
            persons = persons.exclude(user__isnull=True)
        persons = persons.annotate(Count('papers'))
    else:
        if LIST_AUTHORS_BY_PAPERS:
            persons = persons.annotate(Count('papers')).order_by('-papers__count')[:site.authorByContributionCount]
        else:
            persons = persons.filter(user__isnull=False)
    persons = [ x.attach_permissions(request.user) for x in persons]
    c['persons'] = persons
    return render(request,'persons.html',c)


@catcher
def newss_page(request):
    c = default_context_for(request,News)
    c['years'] = [x.year for x in reversed(News.objects.datetimes('creation_time', 'year'))]
    if c['year']:
        c['news'] = News.objects.filter(creation_time__year=c['year']).order_by('-creation_time')
    else:
        c['news'] = News.objects.order_by('-creation_time').filter(creation_time__gt=datetime.datetime.now()-datetime.timedelta(30))[:10]
    for news in c['news']:
        news.attach_permissions(request.user)

    return render(request,'newss.html',c)

@catcher
def events_page(request):
    c = default_context_for(request,Event)
    c['years'] = [x.year for x in reversed(Event.objects.dates('date_from', 'year'))]
    if c['year']:
        c['events'] = Event.objects.order_by('date_from').filter(
            date_from__year=c['year'])
    else:
        c['events'] = Event.objects.order_by('date_from').filter(
            date_from__gte=datetime.date.today())
    for event in c['events']:
        event.attach_permissions(request.user)
    c['events'] = filter(lambda e: (e.editable or not e.hidden), c['events'])
    return render(request,'events.html', c)


@catcher
def seminars_page(request, year=None):
    c = default_context_for(request,Seminar)
    c['years'] = [x.year for x in reversed(Seminar.objects.dates('date', 'year'))]
    seminars_filters = {}
    seminars_filters['type__in'] = ['course', 'seminar']
    if not settings.SHOW_PARENTED_SEMINARS:
        seminars_filters['parent__isnull'] = True
    if c['year']:
        seminars_filters['date__year'] = c['year']
    else:
        seminars_filters['date__gte'] = datetime.date.today()
    c['seminars'] = Seminar.objects.order_by('date', 'time').filter(**seminars_filters)
    for seminar in c['seminars']:
        seminar.attach_permissions(request.user)
    return render(request,'seminars.html', c)


@catcher
def positions_page(request, year=None):
    c = default_context_for(request,Position)
    c['years'] = [x.year for x in reversed(Position.objects.dates('deadline', 'year'))]
    if c['year']:
        c['positions'] = Position.objects.order_by('deadline').filter(deadline__year=c['year'])
    else:
        c['positions'] = Position.objects.order_by('deadline').filter(deadline__gte=datetime.date.today())
    for position in c['positions']:
        position.attach_permissions(request.user)
    return render(request,'positions.html', c)

@catcher
def users_page(request):
    c = default_context_for(request, User)
    if not request.user.is_authenticated:
        raise NotAuthorized()
    if not request.user.can_list(User):
        raise NotAuthorized()
    initial = request.GET.get('letter', None)
    c['initial'] = initial
    c['initials'] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if initial == 'staff':
        users = User.objects.filter(is_staff=True).order_by('username')
    elif initial:
        users = User.objects.filter(username__startswith=initial.lower()).order_by('username')
    else:
        users = User.objects.order_by('username')

    c['users'] = [x.attach_permissions(request.user) for x in users]
    return render(request,'users.html', c)

@catcher
def logs_page(request):
    c = default_context_for(request, User)
    if not request.user.is_authenticated:
        raise NotAuthorized()
    if not request.user.can_list(Log):
        raise NotAuthorized()
    page = int(request.GET.get('page',0))
    logs_per_page = 50
    logs = Log.objects.order_by('-creation_time')[page*logs_per_page:(page+1)*logs_per_page]
    c['logs'] = logs
    return render(request,'logs.html', c)

## PAGINE SINGOLI OGGETTI:

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def normalize_spaces(s):
    return ' '.join(s.split())

def reduce_to_simple_characters(s):
    good = string.ascii_lowercase + string.digits
    return ''.join([c for c in unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii').lower() if c in good])

def arxiv_paper_sync(request, arxiv_id, paper=None):
    if paper is None:
        paper = Paper()
        paper.arxiv_id = arxiv_id
        paper.created_by = request.user
        paper.paper_type = 'preprint'
        paper.update_from_arxiv()
        add_message(request, INFO, "abstract {} has been successfully loaded from arXiv".format(arxiv_id))
    else:
        if not paper.arxiv_id:
            paper.arxiv_id = arxiv_id
            add_message(request, INFO, "abstract {} linked to already existing paper".format(arxiv_id))
        paper.attach_permissions(request.user)
        if not paper.editable:
            add_message(request, ERROR, "you don't have permission to modify already existing paper for abstract {}".format(arxiv_id))
            raise NotAuthorized()
        paper.modified_by = request.user
        paper.update_from_arxiv()
        add_message(request, INFO, "paper for abstract {} has been successfully updated from arXiv".format(arxiv_id))
    return paper

@catcher
def person_page(request, id):
    c = default_context_for(request, Person)
    try:
        person = Person.objects.get(pk=id).attach_permissions(request.user)
    except ObjectDoesNotExist:
        raise NotFound()
    c['person'] = person
    c['papers'] = [x.attach_permissions(request.user) for x in Paper.objects.filter(
        hidden=False,
        authors=person).order_by('-year')]
    c['seminars'] = [x.attach_permissions(request.user) 
        for x in person.seminars.filter(
            hidden=False
            ).order_by('-date')]
    c['speaker_events'] = [
        x.attach_permissions(request.user) for x in Event.objects.filter(
            hidden=False,
            speakers=person
            ).order_by('-date_from')]
    c['organizer_events'] = [
        x.attach_permissions(request.user) for x in Event.objects.filter(
            hidden=False,
            organizers=person
            ).order_by('-date_from')]
    path = request.path.split('/')[3:]
    if path[0] == 'arxiv':
        if request.POST.get('set_arxiv_id'):
            arxiv_id = request.POST.get('arxiv_id')
            if person.arxiv_id != arxiv_id:
                person.arxiv_id = arxiv_id
                person.save()
                add_message(request, INFO, 'arxiv_id changed')
            else:
                add_message(request, INFO, 'arxiv_id unchanged')

        from .data_import import get_arxiv_author_abstracts, get_arxiv_author_id_abstracts
        arxiv_id_re = re.compile(r'(.*)v(\d+)')
        c['abstracts'] = []
        try:
            if person.arxiv_id:
                c['abstracts'] = get_arxiv_author_id_abstracts(person.arxiv_id)
                c['person_arxiv_query'] = 'arxiv_id:{}'.format(person.arxiv_id)
            else:
                if person.orcid_id:
                    c['abstracts'] = get_arxiv_author_id_abstracts(person.orcid_id)
                    if c['abstracts']:
                        c['person_arxiv_query'] = 'arxiv_id:{}'.format(person.orcid_id)
                if not c['abstracts']:
                    arxiv_query = strip_accents("{} {}".format(person.lastname, person.firstname).replace(' ', '_'))
                    c['abstracts'] = get_arxiv_author_abstracts(arxiv_query)
                    c['person_arxiv_query'] = 'au:{}'.format(arxiv_query)
        except ArxivError as e:
            add_message(request, ERROR, 'Arxiv request error ({})'.format(e))

        c['abstracts'].sort(key=lambda d: d['published'])
        c['abstracts'].reverse()

        # connect papers with arxiv_id
        c['arxiv_papers'] = dict([(p.arxiv_id, p) for p in Paper.objects.filter(authors=person).exclude(arxiv_id='')])
        # add arxiv_id of different version

        for abs in c['abstracts']:
            arxiv_id = abs.get('id')
            m = arxiv_id_re.match(arxiv_id)
            if m:
                base_id, ver = m.groups()
                if base_id in c['arxiv_papers']:
                    c['arxiv_papers'][arxiv_id] = c['arxiv_papers'][base_id]

        # connect papers without arxiv_id but same title
        title_papers = dict([(reduce_to_simple_characters(p.title), p) for p in Paper.objects.filter(authors=person,arxiv_id='')])
        for abs in c['abstracts']:
            lower_title = reduce_to_simple_characters(abs.get('title', ''))
            if lower_title in title_papers and not abs.get('id') in c['arxiv_papers']:
                c['arxiv_papers'][abs.get('id')] = title_papers[lower_title]

        if request.method == 'POST':
            arxiv_ids = request.POST.getlist('arxiv_id')
            log(request.user, "arxiv update arxiv_ids", arxiv_ids)
            count = 0
            for abs in c['abstracts']:
                arxiv_id = abs['id']
                if not arxiv_id in arxiv_ids:
                    continue
                count += 1
                m = arxiv_id_re.match(arxiv_id)
                if m:
                    base_arxiv_id = m.groups()[0]  # latest version
                else:
                    base_arxiv_id = arxiv_id

                try:
                    if arxiv_id in c['arxiv_papers']:
                        paper = c['arxiv_papers'][arxiv_id]
                        arxiv_paper_sync(request, base_arxiv_id, paper)
                    else:
                        arxiv_paper_sync(request, base_arxiv_id)
                except RuntimeError as e:
                    add_message(request, ERROR, "while syncing xarchive paper: {}".format(e))
            if count == 0 and request.POST.get('update'):
                add_message(request, ERROR, "no abstract selected")
            raise Redirect(request.path)

        return render(request,'person_arxiv.html', c)
    return render(request,'person.html',c)


@catcher
def paper_page(request, id):
    c = default_context_for(request, Paper)
    try:
        paper = Paper.objects.get(pk=id)
    except ObjectDoesNotExist:
        raise NotFound()
    paper.attach_permissions(request.user)

    if request.method == 'POST':
        if not paper.editable:
            raise NotAuthorized()
        cmd = request.path.split('/')[-1]
        if cmd == 'arxiv':
            log(request.user, "arxiv update paper", [paper.id])
            paper.update_from_arxiv()
            add_message(request, INFO, 'arxiv sync succeded')
            raise Redirect(paper.url())
        else:
            raise InvalidRequest()

    c['paper'] = paper
    if 'info' in request.GET:
        c['info'] = paper.info_list()
    if 'bibtex' in request.GET:
        return render(request,'bibtex.bib', c, content_type='text/plain')
    if 'citeulike' in request.GET:
        return render(request,'citeulike.txt', c, content_type='text/plain')
    c['documents'] = paper.documents.filter(hidden=False)

    return render(request,'paper.html', c)


@catcher
def keyword_page(request, id):
    c = default_context_for(request)
    try:
        keyword = Keyword.objects.get(pk=id)
    except ObjectDoesNotExist:
        raise NotFound()
    c['keyword'] = keyword
    c['papers'] = Paper.objects.filter(keywords=keyword).order_by('-year')
    return render(request,'keyword.html', c)

@catcher
def news_page(request, id):
    c = default_context_for(request, News)
    try:
        news = News.objects.get(pk=id).attach_permissions(request.user)
    except ObjectDoesNotExist:
        raise NotFound()
    c['news'] = news
    if 'info' in request.GET:
        c['info'] = news.info_list()
    return render(request,'news.html', c)

@catcher
def position_page(request, id):
    c = default_context_for(request, Position)
    try:
        position = Position.objects.get(pk=id).attach_permissions(request.user)
    except ObjectDoesNotExist:
        raise NotFound()
    c['position'] = position
    if 'info' in request.GET:
        c['info'] = position.info_list()
    return render(request,'position.html', c)


@catcher
def event_page(request, id):
    c = default_context_for(request, Event)
    try:
        c['event'] = event = Event.objects.get(pk=id).attach_permissions(request.user)
    except ObjectDoesNotExist:
        raise NotFound()
    if event.hidden and not event.editable:
        raise NotFound()

    if 'redirect_to_google_calendar' in request.GET:
        api = get_google_api()
        url = api.get_calendar_event(c['event'].google_id)['htmlLink']
        raise Redirect(url)

    if request.method == 'POST':
        if not event.editable:
            raise NotAuthorized()
        if request.POST.get('crm_update'):
            if not event.crm_id:
                raise InvalidRequest()
            try:
                update_crm_event(event, request_user=request.user)
                add_message(request, INFO, 'event updated from CRM server')
            except IOError:
                add_message(request, ERROR, 'unable to connect to CRM server')
            except Exception as e:
                add_message(request, ERROR, 'exception raised while importing data from CRM server: {}'.format(e))


    if 'info' in request.GET:
        c['info'] = c['event'].info_list()

    c['documents'] = event.documents.filter(hidden=False)
    c['sub_events'] = [x for x in Event.objects.filter(
        hidden=False,
        parent=event)]
    events = [event] + c['sub_events']
    c['participants'] = EventParticipant.objects.filter(event__in=events, state='accepted', hidden=False)
    if request.user.is_authenticated and request.user.can_edit(event):
        c['pending_count'] = EventParticipant.objects.filter(event__in=events).filter(Q(state='requested') | Q(grant_state='requested')).count()
    return dynamic_template_response(request, 'event.html', c, event)

def event_participants_page_manage_form(request, c, event):
    if not (request.user.is_authenticated and request.user.can_edit(event)):
        return

    c['admin_participants'] = EventParticipant.objects.filter(event=event).exclude(state='cancelled').order_by('creation_time')

    if not (request.method == 'POST'):
        return

    selected = [p for p in c['admin_participants'] if ('p%s' % p.id) in request.POST]
    action = request.POST.get('action')

    if not selected:
        add_message(request, ERROR, 'No participant selected')
        return

    qs = c['admin_participants'].filter(id__in=[x.id for x in selected])

    if action == 'confirm':
        d = {'state': 'accepted'}
    elif action == 'ignore':
        d = {'state': 'cancelled'}
    elif action == 'confirm_grant':
        d = {'grant_state': 'granted'}
    elif action == 'reject_grant':
        d = {'grant_state': 'rejected'}
    elif action == '':
        add_message(request, ERROR, 'No action selected')
        c['admin_selection'] = selected
        return
    else:
        add_message(request, ERROR, 'Invalid action %s' % action)
        return

    count = qs.count()
    qs.update(**d)
    add_message(request, SUCCESS, '%s rows updated' % count)

    if request.POST.get('send_email'):
        emails = []
        for p in qs:
            if not p.email:
                continue
            message = EmailMessage(to=[p.email])
            message.render_template('mail/participant_notification.mail', {'person': p, 'event': event, 'action': action, 'settings': settings})
            message.send()
            emails.append(p.email)
        if emails:
            add_message(request,SUCCESS,'Email sent to: %s' % ', '.join(emails))
        else:
            add_message(request,WARNING,'No email sent')
    raise Redirect(request.path)


@catcher
def event_participants_page(request, event_id):
    c = default_context_for(request,Event)
    try:
        c['event'] = event = Event.objects.get(pk=event_id).attach_permissions(request.user)
    except ObjectDoesNotExist:
        raise NotFound()

    event_participants_page_manage_form(request, c, event)

    if request.user.is_authenticated and request.user.can_edit(event):
        if request.GET.get('xls'): # and request.user.is_staff:
            from .excel import xls_response
            return xls_response('event_participants.xml', c, event)

    return dynamic_template_response(request, 'event_participants.html', c, event)


@catcher
def event_speakers_page(request, event_id):
    c = default_context_for(request, Event)
    try:
        c['event'] = event = Event.objects.get(pk=event_id).attach_permissions(request.user)
    except ObjectDoesNotExist:
        raise NotFound()

    speakers = list(event.speakers.all())
    for speaker in speakers:
        speaker.event = event
    subevents = False
    for subevent in Event.objects.filter(parent=event):
        lst = list(subevent.speakers.all())
        for speaker in lst:
            speaker.event = subevent
        speakers += lst
        subevents = True
    if 'csv' in request.GET:
        fields = ['lastname', 'firstname', 'email', 'affiliation']
        if subevents:
            fields = ['event__id']+fields
        return CsvResponse(speakers, fields)
    c['speakers'] = speakers
    c['subevents'] = subevents
    return dynamic_template_response(request, 'event_speakers.html', c, event)


@catcher
def event_registration_page(request, event_id):
    c = default_context_for(request, Event)
    try:
        c['event'] = event = Event.objects.get(pk=event_id).attach_permissions(request.user)
    except ObjectDoesNotExist:
        raise NotFound()

    if not event.registration_is_open():
        raise NotFound()

    if request.method == 'POST':
        c['form'] = EventRegistrationForm(request.POST, request.FILES, event=c['event'])
        if c['form'].is_valid():
            participant = c['form'].save(commit=False)
            participant.event = c['event']
            participant.state = 'requested'
            if request.user.is_authenticated and request.user.person and request.user.person.lastname == participant.lastname and request.user.person.firstname == participant.firstname:
                participant.person = request.user.person
            participant.save()
            c['form'].save_m2m()
            add_message(request, SUCCESS, 'Your registration has been acknowledged. You will receive a confirmation as soon as possible.')
            return HttpResponseRedirect('.') # event
        else:
            add_message(request,ERROR,'The form contains errors')
    else:
        person = None
        if request.user.is_authenticated:
            try:
                person = request.user.person
            except Person.DoesNotExist:
                pass # maybe it is root...
        c['form'] = EventRegistrationForm(event=c['event'], person=person)

    return dynamic_template_response(request, 'event_registration.html', c, event)


@catcher
def event_timetable_page(request, event_id):
    c = default_context_for(request, Event)
    try:
        c['event'] = event = Event.objects.get(pk=event_id).attach_permissions(request.user)
    except ObjectDoesNotExist:
        raise NotFound()

    return dynamic_template_response(request, 'event_timetable.html', c, event)

@catcher
def seminar_page(request, id):
    c = default_context_for(request,Seminar)
    try:
        c['seminar'] = seminar = Seminar.objects.get(pk=id).attach_permissions(request.user)
        c['speakers'] = [x.attach_permissions(request.user) for x in c['seminar'].speakers.all()]
    except ObjectDoesNotExist:
        raise NotFound()

    if 'redirect_to_google_calendar' in request.GET:
        google_id = c['seminar'].google_id
        if google_id:
            api = get_google_api()
            url = api.get_calendar_event(google_id)['htmlLink']
            raise Redirect(url)
        else:
            add_message(request, ERROR, "seminar is not linked to google calendar")

    if 'info' in request.GET:
        c['info'] = c['seminar'].info_list()
    c['documents'] = seminar.documents.filter(hidden=False)
    return dynamic_template_response(request, 'seminar.html', c, seminar)
    return render(request,'seminar.html', c)

## PAGINE UTENTI
@catcher
def login_page(request, next=None):
    c = default_context_for(request)
    next = request.GET.get('next', next) or ROOT_URL
    as_user = request.GET.get('as')
    username = request.POST.get('username', None)
    if request.user.is_authenticated:
        add_message(request, WARNING, 'you are already logged in!')
    if username or request.POST.get('submit', None):
        if request.POST.get('sendpasswd', False):
            try:
                user = User.objects.get(username=username)
                if user.person and user.person.email:
                    send_new_password(user, request)
                    add_message(request, SUCCESS, 'A new password has been sent to the email address: {}'.format(user.person.email))
                else:
                    add_message(request, ERROR, 'User has no email configured')
            except User.DoesNotExist:
                add_message(request, ERROR, 'Invalid username')
        else:
            password = request.POST.get('password', '')
            if as_user is None:
                user = authenticate(username=username, password=password)
            else:
                user = authenticate(admin=username, password=password, as_user=as_user)
            if user and user.can_login():
                login(request,user)
                add_message(request, SUCCESS, 'You have logged in')
                log(user, "logged in")
            else:
                add_message(request, ERROR, 'Invalid user or password')
                log(request.user, "invalid user or password in login")
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect(next)
    return render(request,'login.html', c)


@catcher
def logout_page(request, next=None):
    next = request.GET.get('next',next) or ROOT_URL
    user = request.user
    username = user.username
    logout(request)
    add_message(request,INFO,'user %s logged out' % username)
    log(user,"logged out")
    return HttpResponseRedirect(next)

@catcher
def passwd_page(request, user_id=None):
    check_authenticated_user(request)
    c = default_context_for(request)
    if user_id:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise NotFound()
    else:
        user = request.user

    if user != request.user:
        raise NotAuthorized()

    class PasswdForm(forms.Form):
        old_password = forms.CharField(widget=forms.PasswordInput)
        new_password = forms.CharField(widget=forms.PasswordInput)
        new_password_again = forms.CharField(widget = forms.PasswordInput)

    if request.method == 'POST':
        form = PasswdForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            ok = True
            if not user.check_password(d['old_password']):
                add_message(request, ERROR, 'Old password is not valid. Check again')
                ok = False
            if d['new_password'] != d['new_password_again']:
                add_message(request, ERROR, 'The new password must be written twice the same')
                ok = False
            if ok:
                user.set_password(d['new_password'])
                user.save()
                add_message(request, SUCCESS, 'password changed')
                log(user, "changed password", [user])
                raise Redirect(ROOT_URL)

    else:
        form = PasswdForm()

    c['form'] = form

    return render(request,'passwd.html', c)

model_dict = {'paper': Paper,
              'person': Person,
              'news': News,
              'seminar': Seminar,
              'event': Event,
              'position': Position,
              'user': User,
             }

@catcher
def edit_page(request, model_name, id=None):
    try:
        Model = model_dict[model_name]
    except KeyError:
        raise NotFound()

    check_authenticated_user(request)

    # if False and request.user.username != 'paolini':
    #     add_message(request,ERROR,'the server is in maintenance mode: cannot modify data for a while... sorry')
    #     raise Redirect(ROOT_URL)

    c = default_context_for(request)
    c['name'] = model_name.title()
    c['code'] = model_name

    obj = None

# CHECK PERMISSIONS

    if id:
        try:
            obj = Model.objects.get(pk=id)
        except ObjectDoesNotExist:
            raise NotFound()
        if not request.user.can_edit(obj):
            raise NotAuthorized()
        c['object'] = obj
    else:
        if not request.user.can_create(Model):
            raise NotAuthorized()

# CHECK USER INPUT
    action = request.POST.get('action',None)
    if not action:
        pass
    elif action == 'crm_import' and model_name == 'event':
        if False and not request.user.is_staff:
            raise NotAuthorized()
        from .data_import import get_crm_event
        try:
            crm_id = int(request.POST['crm_id'])
        except ValueError:
            add_message(request, ERROR, 'invalid crm id')
            raise Redirect(request.get_full_path())
        c['crm_id'] = crm_id
        try:
            event = Event.objects.get(crm_id=crm_id)
            event.attach_permissions(request.user)
            if not event.editable:
                add_message(request, ERROR, "you don't have permission to modify the already existing event")
                raise NotAuthorized()
        except Event.DoesNotExist:
            pass  # anyone can create a new event
        log(request.user, 'import event from crm', [crm_id])
        try:
            event = get_crm_event(crm_id, request_user=request.user)
            add_message(request, SUCCESS, 'event imported from crm')
            return HttpResponseRedirect(ROOT_URL+'event/%d/' % event.id)
            c['import_message'] = event
        except Exception as e:
            add_message(request, ERROR, 'exception raised while importing. {}'.format(e))
    elif action == 'arxiv_import' and model_name == 'paper':
        from .data_import import get_arxiv_abstract
        arxiv_id = request.POST['arxiv_id']
        if not arxiv_id:
            add_message(request, ERROR, 'arxiv_id required')
        else:
            log(request.user,"arxiv import arxiv_id",[arxiv_id])
            try:
                paper = Paper.objects.get(arxiv_id=arxiv_id)
                arxiv_paper_sync(request, arxiv_id, paper)
            except Paper.DoesNotExist:
                try:
                    paper = arxiv_paper_sync(request, arxiv_id)
                except ArxivError as e:
                    add_message(request, ERROR, e)
                    paper = None
            if paper:
                raise Redirect(ROOT_URL+'%s/%d/' % ('paper', paper.pk))
    else:
        raise InvalidRequest()

    # CHECK FOR CANCEL BUTTON
    if not action and request.POST.get('cancel', None):
        add_message(request,WARNING,'operation cancelled')
        if obj:
            raise Redirect(ROOT_URL+'%s/%d/' % (model_name, obj.pk))
        else:
            raise Redirect(ROOT_URL)

    # CHECK FOR FORM SUBMISSION
    if not action and request.POST:
        form = getModelForm(Model)(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            saveRelatedFields(form.cleaned_data)
            new_obj = form.save(commit=False)
            if obj:
                new_obj.modified_by = request.user
            else:
                new_obj.created_by = request.user
                if Model == Paper:
                    new_obj.code = new_obj.get_unique_code(
                        form.cleaned_data['authors'],
                        form.cleaned_data['year'])

            if 'event' in request.GET:
                try:
                    event = Event.objects.get(id=request.GET['event'])
                    if not request.user.can_edit(event):
                        raise NotAuthorized()
                    if Model in [Seminar, Event]:
                        new_obj.parent = event
                except Event.DoesNotExist:
                    raise InvalidRequest()

            if isinstance(new_obj, CalendarModel):
                new_obj.save(update_calendar=False)
            else:
                new_obj.save()

            if isinstance(form.instance, Paper):
                try:
                    paper = form.instance
                    PaperAuthor.objects.filter(paper=paper).delete()
                    authors = form.cleaned_data.pop('authors')
                    for order, person in enumerate(authors, start=1):
                        PaperAuthor(person=person,
                                    paper=paper,
                                    order=order).save()

                except KeyError:
                    pass
            form.save_m2m()
            if isinstance(new_obj, CalendarModel):
                new_obj.google_calendar_save()
                add_message(request, SUCCESS, 'event updated in calendar')

            add_message(request,SUCCESS,'%s successfully updated' % model_name)
            log(request.user,"edit or new object", [new_obj])
            if Model == User:
                raise Redirect(ROOT_URL+'users/')
            raise Redirect(ROOT_URL+'%s/%d/' % (model_name,form.instance.pk))
        else:
            add_message(request, ERROR, 'The form is not valid. Please check the errors below and submit again')
    elif obj:
        form = getModelForm(Model)(initial=model_to_dict(obj))
        # form.as_table() ## debugging
    else:
        initial = {'year': datetime.datetime.now().year}
        if 'tag' in request.GET:
            try:
                try:
                    tag = int(request.GET['tag'])
                    tag = Tag.objects.get(pk=tag)
                except (ValueError,TypeError):
                    tag = Tag.objects.get(value__iexact=request.GET['tag'])
            except Tag.DoesNotExist:
                pass
            else:
                initial['tags'] = [tag]
        form = getModelForm(Model)(initial=initial)
    c['form'] = form
    return render(request,'edit_form.html', c)


@catcher
def remove_page(request, model_name, id=None):
    try:
        Model = model_dict[model_name]
    except KeyError:
        raise NotFound()

    check_authenticated_user(request)

    c = default_context_for(request)
    c['name'] = model_name.title()
    c['code'] = model_name

    obj = None

# CHECK PERMISSIONS

    try:
        obj = Model.objects.get(pk=id)
    except Model.DoesNotExist:
        raise NotFound()

    if not request.user.can_delete(obj):
        raise NotAuthorized()
    c['object'] = obj

    if request.POST:
        # CHECK FOR CANCEL BUTTON
        if request.POST.get('cancel', None):
            add_message(request, WARNING, 'operation cancelled')
            raise Redirect(ROOT_URL+'%s/%d/' % (model_name,obj.pk))

        if request.POST.get('remove', None) == 'y' and request.POST.get('confirm', None):
            log(request.user,'delete object', [obj])
            if type(obj) == User:
                l = Person.objects.filter(user=obj)
                for person in l:
                    add_message(request, WARNING, 'person %s now has no associated user' % person)
                    log(request.user, 'user removed from person', [person])
                    person.user = None
                    person.save()
            obj.delete()
            add_message(request, SUCCESS, '%s removed' % model_name)
            raise Redirect(ROOT_URL)
        add_message(request, ERROR, 'request of removal not confirmed')
    return render(request,'remove_form.html', c)


@catcher
def upload_page(request, model_name, id):
    check_authenticated_user(request)
    c = default_context_for(request)

    c['name'] = model_name

    try:
        Model = model_dict[model_name]
    except KeyError:
        raise NotFound()

    try:
        obj = Model.objects.get(pk=id)
    except Model.DoesNotExist:
        raise NotFound()

    if not request.user.can_edit(obj):
        raise NotAuthorized()

    if request.POST:
        ids = request.POST.getlist('id')
        descriptions = request.POST.getlist('description')
        actions = request.POST.getlist('action')
        hidden_flags = [x=='hidden' for x in request.POST.getlist('flag')]
        for n in range(min(len(ids),len(descriptions),len(hidden_flags))):
            if ids[n]:
                ## existing document
                try:
                    doc = obj.documents.get(id=ids[n])
                except Document.DoesNotExist:
                    raise InvalidRequest()
                if doc.description != descriptions[n] or doc.hidden != hidden_flags[n]:
                    doc.description = descriptions[n]
                    doc.hidden = hidden_flags[n]
                    doc.save()
                    add_message(request,SUCCESS,'document description/flags modified')
                elif actions[n] == 'delete':
                    path = doc.file.name
                    doc.delete()
                    ## il file viene rimosso automaticamente
##                    os.remove(os.path.join(MEDIA_ROOT,path))
                    add_message(request,SUCCESS,'file %s deleted' % (os.path.split(path)[1]))
                    log(request.user,"document deleted",path)
            else:
                ## new document
                f = request.FILES.get("file")
                if f:
                    doc = Document()
                    filename = f.name
                    filename = filename[
                        max(0, f.name.rfind('/'), f.name.rfind('\\'))
                        :]
                    while filename[0]=='.':
                        filename = filename[1:]
                    safename = ''
                    for i in range(len(filename)):
                        if filename[i].isalnum() or filename[i] in '_-. ':
                            safename += filename[i]
                        else:
                            safename += '@'

                    ## check if need to replace existing document
                    l = [ x for x in obj.documents.all()
                          if os.path.split(x.file.name)[1] == safename]

                    if l:
                        log(request.user, "replace document",l)
                        l[0].delete()
                        add_message(request, WARNING, 'file replaced')

                    dir = os.path.join('doc', obj.codename(), '%d' % obj.pk)
                    path =  os.path.join(dir, safename)

                    dir = os.path.join(MEDIA_ROOT, dir)
                    if not os.path.exists(dir):
                        os.makedirs(dir)

                    with open(os.path.join(MEDIA_ROOT, path), 'wb') as outfile:
                        for chunk in f.chunks():
                            outfile.write(chunk)
        
                    doc.file = path
                    doc.description = descriptions[n]
                    doc.hidden = hidden_flags[n]
                    if not doc.description:
                        doc.description = path.split('/')[-1].split('\\')[-1]
                    doc.save()

                    obj.documents.add(doc)
                    obj.save()
                    add_message(request, SUCCESS, 'file %s uploaded'%safename)
                    log(request.user, "document added", [obj])

    c['object'] = obj
    documents = list(obj.documents.all())

    for document in documents:
        document.filename = document.file.name.split('/')[-1]
    c['documents'] = documents

    return render(request,'upload_form.html', c)

@catcher
def send_page(request,model_name,id):
    check_authenticated_user(request)
    c = default_context_for(request)

    c['name'] = model_name
    c['user'] = request.user

    try:
        Model = model_dict[model_name]
    except KeyError:
        raise NotFound()
    try:
        obj = Model.objects.get(pk=id)
    except Model.DoesNotExist:
        raise NotFound()

    From = None
    if USE_PERSONAL_EMAIL:
        From = request.user.person.email
    else:
        From = PERSONAL_EMAIL_TEMPLATE.format(
            person=request.user.person,
            config={}) 
    c['object'] = obj
    c['From'] = From

    class SendForm(forms.Form):
        to = forms.EmailField(widget=forms.TextInput(attrs={'size': 80}))
#        cc = forms.EmailField(required=False, widget=forms.TextInput(attrs={'size': 80}))
        subject = forms.CharField(widget=forms.TextInput(attrs={'size': 80}))
        body = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 30}))

    if request.POST:
        form = SendForm(request.POST)
        if form.is_valid():
            # send message
            d = form.cleaned_data
            # from django.core.mail import EmailMessage
            to = d['to'].split(',')
#            cc = d['cc'].split(',')
            args = {
                'subject': d['subject'],
                'body': d['body'],
                'from_email': From,
                'to': to
                }

            email = EmailMessage(**args)
            email.send()
            add_message(request,SUCCESS,'email sent')
            log(request.user,"send email", args)
            raise Redirect(obj.url())
        else:
            # form not valid
            add_message(request,ERROR,'The form is not valid. Please check the errors below and submit again')
    else:
        d = {}
        d['subject'] = '['+SITE_NAME+' %s] %s' % ( model_name, obj.title )
        d['to'] = BULLETIN_EMAIL
        d['cc'] = ''
        body = ''
        body += '%s\n-----------------------------------------\n' % (obj.title)
        body += '\n%s%s\n\n' % (SERVER_URL, obj.url())

        FORMAT = '%A, %h %e, %Y'

        if hasattr(obj,'deadline') and obj.deadline:
            body += 'Deadline: %s\n\n' % obj.deadline.strftime(FORMAT)

        if hasattr(obj,'date_from') and obj.date_from:
            body += 'Date: %s' % obj.date_from.strftime(FORMAT)
            if hasattr(obj,'date_to') and obj.date_to:
                body += ' -- %s' % obj.date_to.strftime(FORMAT)
            body += '\n\n'

        if hasattr(obj,'date') and obj.date:
            body += 'Date: %s\n\n' % obj.date.strftime(FORMAT)

        if hasattr(obj,'time') and obj.time:
            body += 'Time: %s\n\n' % obj.time.strftime('%H:%M')

        if hasattr(obj,'place') and obj.place:
            body += 'Place: %s\n\n' % obj.place

        if type(obj) == Seminar and  obj.speakers:
            pl = ''
            if len(obj.speakers.all()) > 1:
                pl = 's'
            body += 'Speaker%s: %s\n\n' % (pl,', '.join([x.firstname + ' ' + x.lastname for x in obj.speakers.all()]))

        if hasattr(obj,'description'):
            body += '%s\n\n' % (obj.description)

        if hasattr(obj,'abstract'):
            body += 'Abstract. %s\n\n' % (obj.abstract)

        if hasattr(obj,'organizers') and obj.organizers:
            body += 'Organizing Commitee: %s\n\n' % ', '.join([x.short() for x in obj.organizers.all()])

        if type(obj) == Event and obj.speakers:
            body += 'Invited Speakers: %s\n\n' % ', '.join([x.short() for x in obj.speakers.all()])

        if hasattr(obj,'links') and obj.links:
            for link in obj.links.all():
                body += '%s: %s\n\n' % (link.description,link.url)

        if hasattr(obj,'keywords') and obj.keywords.all():
            body += 'Keywords: %s\n\n' % ', '.join([x.name for x in obj.keywords.all()])

        d['body'] = body
        form = SendForm(initial=d)

    c['form'] = form

    return render(request,'send_form.html', c)


@catcher
def old_people_page(request,path):
    username = path.split('/')[0]
    try:
        p = Person.objects.get(user__username=username)
        raise Redirect(ROOT_URL + 'person/%d/' % p.pk)
    except Person.DoesNotExist:
        raise NotFound()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@catcher
def request_page(request):
    c = default_context_for(request)

    #    PersonRequestForm = getModelForm(PersonRequest)
    if request.POST:
        form = PersonRequestForm(request.POST)
        if form.is_valid():
            new_obj = form.save(commit=False)
            new_obj.ip = get_client_ip(request)
            new_obj.save()
            add_message(request, SUCCESS, 'Your request has been filed')
            c['done'] = True
            send_note_to_staff(request, new_obj)
            log(request.user,"account request", [new_obj])
        else:
            add_message(request, ERROR, 'The form is not valid. Please check the errors below and submit again')
    else:
        form = PersonRequestForm()

    c['form'] = form
    template = "request.html"
    return render(request,template, c)


@catcher
def person_requests(request):
    c = default_context_for(request)

    check_authenticated_user(request)
    if not request.user.is_staff:
        raise NotAuthorized()

    requests = [x.attach_permissions(request.user) for x in PersonRequest.objects.filter(managed=False)]
    c['requests'] = requests
    c['managed_requests'] = [x.attach_permissions(request.user) for x in PersonRequest.objects.filter(managed=True).order_by('-creation_time')[:10]]
    return render(request,'person_requests.html', c)


@catcher
def person_request(request, id):
    c= default_context_for(request)

    check_authenticated_user(request)
    if not request.user.is_staff:
        raise NotAuthorized()

    try:
        person_request = PersonRequest.objects.get(id=id)
    except ObjectDoesNotExist:
        raise NotFound()

    ## search for existing person matching request
    persons = Person.objects.filter(lastname=person_request.lastname,
                                    firstname=person_request.firstname)

    c['persons']=[x for x in persons]

    if request.method == 'POST':
        if request.POST.get('reopen', False):
            person_request.managed = False
            person_request.save()
            add_message(request, WARNING, 'request has been set to unmanaged')
            raise Redirect(ROOT_URL + 'person_request/{}/'.format(person_request.id))

        if request.POST.get('ignore', False):
            person_request.managed = True
            person_request.save()
            add_message(request, WARNING, 'Request has been set as managed')
            send_note_to_staff(request, person_request)
            raise Redirect(ROOT_URL + 'person_requests/')

        if request.POST.get('email', False):
            message = EmailMessage(to=person_request.email, from_email=request.user.person.email)
            message.Body = request.POST.get('body')
            message.Subject = request.POST.get('subject')
            message.send()
            if True:  # TODO: check message.send errors?
                person_request.managed = True
                person_request.save()
                add_message(request, WARNING, 'Message has been sent, request set as managed')
                send_note_to_staff(request, person_request)
            else:
                add_message(request, ERROR, 'Error while sending message, request not managed')
            raise Redirect(ROOT_URL + 'person_requests/')

        confirm = request.POST.get('confirm', False)
        if not confirm:
            add_message(request, ERROR, 'operation not confirmed')
            c['request'] = person_request
            return render(request,'person_request.html', c)
        person_id = request.POST.get('person', 0)
        if person_id:
            try:
                person = Person.objects.get(id=person_id)
                if person.email and person.email != person_request.email:
                    add_message(request, WARNING, "changing email: '{}' => '{}'".format(person.email, person_request.email))
                person.email = person_request.email
                if person.affiliation and person_request.affiliation != person.affiliation:
                    add_message(request, WARNING, "changing affiliation: '{}' => '{}'".format(person.affiliation, person_request.affiliation))
                person.affiliation = person_request.affiliation
                person.save()
                log(request.user, "email added to person from person_request",
                    [person_request, person])
            except ObjectDoesNotExist:
                print(("invalid person_id %s " % person_id))
                raise InvalidRequest()
        else:
            person = Person()
            pr = person_request
            person.firstname = pr.firstname
            person.lastname = pr.lastname
            person.affiliation = pr.affiliation
            person.position = pr.position
            person.email = pr.email
            person.save()
            add_message(request, SUCCESS, 'New person created')
            log(request.user, "person created from person_request", [person,person_request])

        user = person.user
        if not user:
            user = User()
            username = person.lastname.lower().replace(' ', '')
            max_length = user._meta.get_field('username').max_length
            i=0
            username_try = username[:max_length]
            while User.objects.filter(username=username_try):
                i += 1
                suffix = "{}".format(i)
                username_try = username[:max_length-len(suffix)] + suffix
            username = username_try

            user.username = username
            user.save()
            person.user = user
            person.save()
            add_message(request, INFO, 'New user and password created')
            log(request.user, "new user created from person_request", [user, person])
        else:
            add_message(request, INFO, 'Changing password of existing user')
        send_new_password(person.user, request, welcome=True)
        add_message(request, INFO, 'An email with account password has been sent to %s' % person.email)
        person_request.managed = True
        person_request.save()
        add_message(request, INFO, 'Request has been marked as managed')
        log(request.user, "person_request managed", [person_request])
        send_note_to_staff(request, person_request)
        
        raise Redirect(ROOT_URL + 'person_requests/')

    c['person_request'] = person_request

    return render(request,'person_request.html', c)


@catcher
def slug_page(request,slug):
    if slug and slug[-1] == '/':
        slug = slug[:-1]
    if slug:
        try:
            event = Event.objects.get(slug__iexact=slug)
            return HttpResponseRedirect(event.url())
        except Event.DoesNotExist:
            pass
    raise NotFound()

@catcher
def default_page(request):
    """
    default view used for pages with no additional information
    see ../urls.py
    """
    c = default_context_for(request)
    #template = str.encode(request.path, 'ascii', 'ignore')
    template = str(request.path)
    if not re.match('^[a-zA-Z0-9_/]*$',template):
        raise SuspiciousOperation(template)
    if template[-1] == '/':
        template = template[:-1]
    if template[0] == '/':
        template = template[1:]
    try:
        return render(request,template, c)
    except TemplateDoesNotExist:
        template += '.html'
        try:
            return render(request,template, c)
        except TemplateDoesNotExist:
            raise NotFound()

@catcher
def paper_list_page(request):
    lst = Paper.objects.all()

    if 'author' in request.GET:
        try:
            lst = lst.filter(authors = request.GET['author'])
        except ValueError:
            raise NotFound()

    lst = lst.order_by('year', 'authors')

    if 'txt' in request.GET:
        s = '\n'.join([paper.txt()
                       for paper in lst])
        return HttpResponse(s.encode('latin1', 'ignore'), content_type='text/plain')

    raise NotFound


def bulletin(context=None):
  now = timezone.now()
  next_week = now + datetime.timedelta(7)
    ## weekday is 0 on monday, 6 on sunday
  next_sunday = next_week + datetime.timedelta(6-next_week.weekday())
  # print "next sunday: %s" % next_sunday

  c = context
  if c is None:
      c={}

  c['settings'] = settings
  seminars_filters = {}
  if not settings.SHOW_PARENTED_SEMINARS:
      seminars_filters['parent__isnull'] = True
  c['seminars'] = Seminar.objects.filter(
    hidden = False,
    date__gte = now,
    date__lte = next_sunday,
    type__in = ['seminar', 'course'],
    **seminars_filters).order_by('date', 'time')
  c['events'] = Event.objects.filter(
    hidden = False,
    date_from__gte = now,
    date_from__lte = next_sunday,
    ).order_by('date_from')

  last_week_start = now - datetime.timedelta(7)
  last_week_end = last_week_start + datetime.timedelta(7)
#  print("last week: ", last_week_start, last_week_end)
  c['last_week_start'] = last_week_start.date()
  c['last_week_end'] = last_week_end.date()

  c['news'] = News.objects.filter(
    hidden = False,
    creation_time__gte=last_week_start,
    creation_time__lt=last_week_end
    ).order_by('creation_time')

  c['new_papers'] = list (Paper.objects.filter(
    hidden = False,
    creation_time__gte=last_week_start,
    creation_time__lt=last_week_end
    ).order_by('creation_time'))
  
  c['modified_papers'] = [x for x in list(Paper.objects.filter(
    hidden = False,
    modification_time__gte=last_week_start,
    modification_time__lt=last_week_end))
        if not x in c['new_papers']]

  c['positions'] = Position.objects.filter(
    hidden = False,
    deadline__gte = datetime.datetime.now()
    ).order_by('deadline')

  def authors(papers):
      lst = set()
      for paper in papers:
          for author in paper.authors.all():
              lst.add(author)
      return lst

  for field in ('new_papers', 'modified_papers'):
      c[field+'_authors'] = authors(c[field])

  return c

@catcher
def bulletin_page(request):
    c = default_context_for(request)
    c = bulletin(c)
    return render(request,'bulletin.html', c)

@catcher
def text_bulletin_page(request):
    c = default_context_for(request)
    c = bulletin(c)
    return render(request,'mail/bulletin.mail', c, content_type='text/plain; charset=utf-8')

def test_messages_page(request):
    c = default_context_for(request)
    add_message(request, SUCCESS, 'success message')
    add_message(request, INFO, 'information message')
    add_message(request, WARNING, 'warning message')
    add_message(request, ERROR, 'error message')
    return render(request,'base.html', c)

def robots_page(request):
    return HttpResponse("""
User-agent: *
Disallow: /login
""", content_type="text/plain")

@catcher
def upload_curriculum_page(request):
    from .forms import CurriculumForm
    if not request.user.is_staff:
        raise NotFound
    c = default_context_for(request)

    if request.method == 'POST':
        form = CurriculumForm(request.POST, request.FILES)
        if form.is_valid():
            lst=EventParticipant.objects.filter(email=form.cleaned_data['email'])
            for participant in lst:
                assert participant.documents.all().count() == 0
                document = Document(file=form.cleaned_data['file'], description='curriculum')
                document.upload_to = os.path.join('doc', participant.codename(), '%d' % participant.pk)
                document.save()
                participant.documents.add(document)
                participant.save()
                add_message(request, ERROR, 'document added to request %s' % participant)
            if not lst:
                add_message(request, ERROR, 'no request matching given email')
        else:
            add_message(request, ERROR, 'errors in form')
    else:
        form = CurriculumForm()
    c['form'] = form
    return render(request,'upload_curriculum.html', c)

def autocomplete_lastname(request):
    if not request.user.is_authenticated:
        raise NotAuthorized()

    lastname = request.GET.get('lastname', '').strip()
    if lastname:
        lst = list(set([x + ', ' + y for (x,y) in Person.objects.filter(lastname__istartswith=lastname).values_list('lastname', 'firstname')]))
    else:
        lst = []
    return JsonResponse(lst, safe=False)

def autocomplete_firstname(request):
    if not request.user.is_authenticated:
        raise NotAuthorized()

    lastname = request.GET.get('lastname', None).strip()
    firstname = request.GET.get('firstname', '').strip()
    if lastname and firstname:
        lst = list(set([x for (x,) in Person.objects.filter(lastname=lastname, firstname__istartswith=firstname).values_list('firstname')]))
    else:
        lst = []
    return JsonResponse(lst, safe=False)

def autocomplete_paper_type(request):
    lst =  Paper.objects.values('paper_type').annotate(count=Count('id')).order_by('-count')
    lst = [x['paper_type'] for x in lst[:10]]
    lst = [x for x in lst if x]
    return JsonResponse({'lst': lst})

def autocomplete_position(request):
    lst =  Person.objects.values('position').annotate(count=Count('id')).order_by('-count')
    lst = [x['position'] for x in lst[:10]]
    lst = [x for x in lst if x]
    return JsonResponse({'lst': lst})

def version_page(request):
    import django
    import subprocess
    import sys
    from django.conf import settings

    c = default_context_for(request)
    info = c['version_info'] = {}
    info['django_version'] = django.__version__
    info['piprints_version'] = subprocess.check_output(['git', 'describe', '--tags'], cwd=settings.BASE_ROOT)
    info['python_version'] = sys.version
    info['python_virtualenv'] = sys.prefix


    return render(request,'version.html', c)

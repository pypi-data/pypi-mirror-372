import urllib.request, urllib.parse, urllib.error
import json
import datetime
import requests
import dateutil.parser
import xml.etree.ElementTree
import re

class ImportError(RuntimeError):
    pass

CRM_URL = 'http://crm.sns.it'

def get_crm_dict(name,crm_id):
    return json.loads(urllib.request.urlopen(CRM_URL + '/%s/%d/index.json' %
                                         (name,crm_id)).read())

def get_crm_person(crm_id, request_user=None):
    from .models import Person
    try:
        person = Person.objects.get(crm_id = crm_id)
    except Person.DoesNotExist:
        d = get_crm_dict('person',crm_id)
        try:
            person = Person.objects.get(lastname = d['lastname'],
                                        firstname = d['firstname'])
            person.crm_id = crm_id
            person.save()

        except Person.DoesNotExist:
            person = Person()
            if request_user:
                person.created_by = request_user
            person.crm_id = crm_id
            for field in ['lastname','firstname','affiliation']:
                setattr(person,field,d[field])
            person.save()
        except Person.MultipleObjectsReturned:
            raise ImportError("Ambiguous name (multiple objects) for person {} {}".format(d['firstname'], d['lastname']))
    return person

def crm_date(s):
    return datetime.date(int(s[0:4]),int(s[5:7]),int(s[8:10]))

def crm_time(s):
    return datetime.time(*map(int,s.split(':')[0:2]))

def crm_id_from_code(crm_code):
    return int(crm_code.split('/')[2])

def get_crm_course(crm_id, request_user=None):
    from .models import Seminar
    try:
        seminar = Seminar.objects.get(crm_id = crm_id)
    except Seminar.DoesNotExist:
        seminar = Seminar()
        seminar.crm_id = crm_id
        if request_user:
            seminar.created_by = request_user
    d = get_crm_dict('course', crm_id)
    if d['type'] in ['talk', 'seminar', 'course']:
        seminar.title = d['title']
        seminar.abstract = d['abstract']
        try:
            from .models import Event
            seminar.parent = Event.objects.get(crm_id = crm_id_from_code(d['event']))
        except Event.DoesNotExist:
            pass
        seminar.type = {'talk': 'seminar', 'seminar': 'seminar', 'course': 'course'}[d['type']]
        if d['lessons']:
            lesson_id = crm_id_from_code(d['lessons'][0]) # considero la prima lezione
            dd = get_crm_dict('lesson', lesson_id) 
            seminar.date = crm_date(dd['date'])
            seminar.time = crm_time(dd['begin_time'])
        seminar.save(update_calendar=False)
        seminar.speakers.set([get_crm_person(crm_id_from_code(person_code), request_user=request_user) for person_code in d['speakers']])
        seminar.google_calendar_save()

    elif d['type'] == 'course':
        return None 
    else:
        return None # breaks and communications
    return seminar

def update_crm_event(event, crm_dict=None, request_user=None):
    assert event.crm_id
    if crm_dict is None:
        crm_dict = get_crm_dict('event', event.crm_id)
    for field in ['title','description']:
        setattr(event, field, crm_dict[field])
    for field, attr in [('begin_date', 'date_from'), ('end_date', 'date_to')]:
        setattr(event, attr, crm_date(crm_dict[field]))
    event.place = 'Pisa: Centro De Giorgi'
    event.save(update_calendar=False)

    event.organizers.set([get_crm_person(crm_id_from_code(person_code),request_user=request_user)
                        for person_code in crm_dict.get('organizers',[])])

    event.speakers.set([get_crm_person(crm_id_from_code(person_code),request_user=request_user)
                for person_code in crm_dict.get('speakers',[])])

    for course_code in crm_dict.get('courses', []):
        get_crm_course(crm_id_from_code(course_code),request_user=request_user)
    
    event.google_calendar_save()


def get_crm_event(crm_id, crm_dict=None, request_user=None):
    from .models import Event, Person
    try:
        event = Event.objects.get(crm_id = crm_id)
    except Event.DoesNotExist:
        d = get_crm_dict('event', crm_id)
        try:
            event = Event.objects.get(title=d['title'],
                                      date_from=datetime.date(*list(map(int,d['begin_date'].split('-')))))
            event.crm_id = crm_id
            event.save()
        except (Event.DoesNotExist, ValueError, TypeError):
            event = Event()
            if request_user:
                event.created_by = request_user
            event.crm_id = crm_id
            update_crm_event(event, crm_dict, request_user)
    return event

class ArxivError(RuntimeError):
    pass

tag_re = re.compile(r'{.*}(.*)')
arxiv_id_re = re.compile(r'https?://arxiv.org/abs/(.*)')
arxiv_id_error = re.compile(r'.*api/errors#(.*)$')

def arxiv_parse_xml(text):
    def tag(e):
        return tag_re.match(e.tag).groups()[0]

    tree = xml.etree.ElementTree.fromstring(text)
    lst = []
    for e1 in tree:
        if tag(e1) == 'entry':
            d = {}
            for e2 in e1:
                t = tag(e2)
                if t == 'id':
                    m = arxiv_id_error.match(e2.text)
                    if m:
                        raise ArxivError(m.groups()[0].replace('_', ' '))
                    d['id'] = arxiv_id_re.match(e2.text).groups()[0]
                elif t in ['updated', 'published']:
                    d[t] = dateutil.parser.parse(e2.text)
                elif t in ['title', 'summary', 'primary_category']:
                    s = e2.text
                    if s:
                        ## sometimes e2.text is a str and sometimes is a unicode!
                        if not isinstance(s, str):
                            s = str(s, 'utf8')
                        d[t] = s

                elif t == 'author':
                    if not t+'s' in d:
                        d[t+'s'] = []
                    for e3 in e2:
                        if tag(e3) == 'name':
                            d[t+'s'].append(e3.text)
                        else:
                            print(('*', tag(e3)))
                elif t == 'link':
                    if 'title' in e2.attrib:
                        d['pdf_url'] = e2.attrib['href']
                elif t in ['primary_category', 'category']:
                    if not 'categories' in d:
                        d['categories'] = []
                    d['categories'].append(e2.attrib['term'])
            lst.append(d)
    return lst

def get_arxiv_abstract(arxiv_id):
    r = requests.get('http://export.arxiv.org/api/query?id_list={}'.format(arxiv_id))
    (d,) = arxiv_parse_xml(r.content)
    return d

def get_arxiv_author_abstracts(au_keyword):
    try:
        r = requests.get('http://export.arxiv.org/api/query?search_query=au:+{}'.format(au_keyword))
    except requests.ConnectionError as e:
        raise ArxivError("connection error")
    lst = arxiv_parse_xml(r.text.encode('utf8'))
    return lst

def get_arxiv_author_id_abstracts(author_id):
    url = 'https://arxiv.org/a/{}.atom'.format(author_id)
    r = requests.get(url)
    try:
        lst = arxiv_parse_xml(r.text.encode('utf8'))
    except xml.etree.ElementTree.ParseError:
        raise ArxivError("unable to load data for author_id: {}".format(author_id)) 
    return lst

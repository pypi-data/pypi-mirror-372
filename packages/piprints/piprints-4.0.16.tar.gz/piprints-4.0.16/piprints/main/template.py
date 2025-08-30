from piprints.settings import TEMPLATES, DATE_FORMAT, TIME_FORMAT
from . import templatetags
tags = templatetags.piprints
from piprints.main.models import Template, Event, Seminar

from django.template.loaders.base import Loader
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.utils import dateformat

import jinja2
import os
import urllib.request, urllib.parse, urllib.error

def get_parent(obj):
    try:
        return obj.parent
    except AttributeError:
        return None

class JinjaLoader(jinja2.BaseLoader):
    def get_source(self, environment, template):
        root_obj = environment.root_object
        while root_obj:
            if isinstance(root_obj, Event):
                try:
                    db_template = Template.objects.get(event = root_obj, name=template, hidden=False)

                    def refreshed(obj):
                        if obj:
                            Model = type(obj)
                            try:
                                obj = Model.objects.get(id=obj.id)
                            except Model.DoesNotExist:
                                obj = None
                        return obj

                    def compute_signature(root_obj,template_obj,refresh=True):
                        if refresh:
                            root_obj = refreshed(root_obj)
                            template_obj = refreshed(template_obj)
                        return (root_obj and root_obj.modification_time,template_obj and template_obj.modification_time)
                    signature = compute_signature(environment.root_object,db_template,refresh=False)
                    return (db_template.source, None,
                            lambda: signature == compute_signature(environment.root_object,db_template))
                except Template.DoesNotExist:
                    pass
            root_obj = get_parent(root_obj)
        for template_dir in TEMPLATES[0]['DIRS']:
            path = os.path.join(template_dir, template)
            if os.path.exists(path) and os.path.isfile(path):
                break
        else:
            raise jinja2.TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        with file(path) as f:
            source = f.read().decode('utf-8')
        return source, path, lambda: mtime == os.path.getmtime(path)
    
    def get_template_sources(self, template_name):
        raise RuntimeError("this must be implemented!")


def flatten_context(context):
    if hasattr(context,'dicts'):
        r = {}
        for d in context.dicts:
            r.update(flatten_context(d))
        return r
    return context

class JinjaTemplate(jinja2.Template):
    def render(self, context):
        # flatten the Django Context into a single dictionary.
        context_dict = flatten_context(context)
        return super(JinjaTemplate, self).render(context_dict)

class MyEnvironment(jinja2.Environment):
    def __init__(self,root_object = None, *args, **kwargs):
        self.root_object = root_object
#        super(MyEnvironment,self).__init__(loader=JinjaLoader(),trim_blocks=True)
        super(MyEnvironment,self).__init__(*args, **kwargs)
        self.template_class = JinjaTemplate

        # These are available to all templates.
        self.globals['url_for'] = reverse
        self.globals['MEDIA_URL'] = settings.MEDIA_URL
        self.globals['STATIC_URL'] = settings.STATIC_URL
        self.globals['facebook_like'] = tags.facebook_like

        self.filters['date'] = lambda d,format=DATE_FORMAT: dateformat.format(d,format)
        self.filters['time'] = lambda d,format=TIME_FORMAT: dateformat.time_format(d,format)
        self.filters['urlencode'] = lambda d: urllib.parse.quote(d.encode('utf8'))
        for name, func in list(tags.__dict__.items()):
            # TODO: check type(func)...
            self.filters[name] = func

class DjangoLoader(Loader):
    is_usable = True
    env = MyEnvironment()

    def load_template(self, template_name, template_dirs=None):
        # obsoleta? forse non viene più
        try:
            template = self.env.get_template(template_name)
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)
        return template, template.filename

    def get_template_sources(self, template_name):
        try:
            template = self.env.get_template(template_name)
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)
        return [template_name]

    
_dynamic_template_cache = {}

def dynamic_template_response(request, template_name,context,root_obj=None):
    # local import to avoid circular dependencies
    # see: https://code.djangoproject.com/ticket/34220
    from django.shortcuts import render
    return render(request, template_name, context)

#   codice disabilitato perche' non sta piu' funzionando...
#   tutto l'ambaradan dei template dinamici non viene più utilizzato...

    env = _dynamic_template_cache.setdefault(root_obj,MyEnvironment(root_obj))
    template = env.get_template(template_name)
    return HttpResponse(template.render(context))

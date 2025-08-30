import os, sys

from time import sleep

from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

from piprints.main.models import SiteParameters, Event, Seminar
from piprints.main import google

def iterate_progress(lst, out=sys.stdout):
    count = len(lst)

    width = 50
    def bar(i):
        n = int(width * 1.0 * i / (count or 1) + 0.5)
        return "[" + "*"*n + " "*(width-n) + "]"

    lastbar = bar(0)
    out.write(lastbar)
    
    for (i, x) in enumerate(lst):
        yield x
        b = bar(i+1)
        if b != lastbar:
            out.write(b+" ({}/{})\r".format(i, count))
            lastbar = b
    out.write('\n')
    

class Command(BaseCommand):
    help = """manage google calendar integration"""
    

    def add_arguments(self, parser):
        parser.add_argument('cmd',
                            choices=[
                                'info',
                                'load_credentials',
                                'set_calendar_id',
                                'create_calendar',
                                'populate_calendar',
                                'delete_calendar',
                                'clear_calendar',
                            ],
                            default='info',
                            help="load_credentials: load service account credentials from JSON file, create_calendar: create new calendar to store events, populate_calendar: insert/update all events from the database to the calendar")
        parser.add_argument('arg', default='', nargs='?')
        parser.add_argument('--force',
                            help="force overwriting",
                            default=False,
                            action='store_true')

    def get_site(self):
        return SiteParameters.objects.get(id=settings.SITE_ID)
        
    def handle(self, cmd, arg, force, **options):
        site = self.get_site()
        
        if cmd == 'info':
            for key in ['service_account_credentials_json', 'calendar_id']:
                self.stdout.write('{}: {}\n'.format(key, getattr(site, 'google_' + key)))
            api = site.get_google_api()
            if api:
                calendar=api.get_calendar()
                self.stdout.write('calendar: {}\n'.format(calendar))
                self.stdout.write('all calendars: {}\n'.format(', '.join(["{}: {}".format(c['id'], c['summary']) for c in api.iterate_calendars()])))
            else:
                self.stdout.write('google apis not configured\n')
                
        elif cmd == 'load_credentials':
            if site.google_service_account_credentials_json and not force:
                self.stderr.write('credentials already exist, use --force to overwrite\n')
                return
            if not arg:
                self.stderr.write('no filename provided\n')
                return
            site.google_service_account_credentials_json = open(arg).read()
            site.save(update_fields=['google_service_account_credentials_json'])
            
        elif cmd == 'set_calendar_id':
            if site.google_calendar_id and not force:
                self.stderr.write('calendar id already exists, use --force to overwrite\n')
                return
            site.google_calendar_id = arg
            site.save(update_fields=['google_calendar_id'])            

        elif cmd == 'create_calendar':
            if site.google_calendar_id and not force:
                self.stderr.write('calendar id already exists, use --force to overwrite\n')
                return
            api = site.get_google_api()
            if not api:
                self.stderr.write('google apis not configured, please set credentials')
                return
            site.google_calendar_id = api.create_calendar()
            site.save(update_fields=['google_calendar_id'])

        elif cmd == 'populate_calendar':
            api = site.get_google_api()
            if not api:
                self.stderr.write('google apis not configured, please set credentials')
                return
            for T in [Event, Seminar]:
                self.stdout.write("writing {}...\n".format(T._meta.verbose_name_plural))
                for obj in iterate_progress(T.objects.filter(google_id=''), self.stdout):
                    obj.google_calendar_save(api=api)
                
        elif cmd == 'delete_calendar':
            if not force:
                self.stderr.write('are you sure you want to delete the calendar? Then use --force')
                return
            api = site.get_google_api()
            api.delete_calendar()
            site.google_calendar_id=''
            site.save(update_fields=['google_calendar_id'])

        elif cmd == 'clear_calendar':
            if not force:
                self.stderr.write('are you sure you want to delete all events in the calendar? Then use --force')
                return
            api = site.get_google_api()
            for event in iterate_progress(list(api.iterate_calendar_events())):
                google_id = event['id']
                api.calendar_delete_event(google_id)
                Seminar.objects.filter(google_id=google_id).update(google_id='')
                Event.objects.filter(google_id=google_id).update(google_id='')
            

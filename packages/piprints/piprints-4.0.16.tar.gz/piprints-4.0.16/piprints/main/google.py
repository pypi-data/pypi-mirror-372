import httplib2
import os
import json

from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

import datetime

CALENDAR_SCOPES = 'https://www.googleapis.com/auth/calendar'

def iterate_google_list(whatever, **kwargs):
    page_token = None
    d = {}
    while True:
        lst = whatever.list(pageToken=page_token, **kwargs).execute()
        for entry in lst['items']:
            yield entry
        page_token = lst.get('nextPageToken')
        if not page_token:
            break

class GoogleApi(object):
    def __init__(self, service_account_credentials_json, calendar_id=None):
        self.service_account_credentials = json.loads(service_account_credentials_json)
        self.calendar_id = calendar_id
        
    def get_calendar_credentials(self):
        """Gets credentials of a google service account
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.service_account_credentials, scopes=CALENDAR_SCOPES)
        return credentials

    def get_calendar_service(self):
        if not hasattr(self, '_service'):
            credentials = self.get_calendar_credentials()
            http = credentials.authorize(httplib2.Http())
            self._service = discovery.build('calendar', 'v3', http=http)
        return self._service
    
    def iterate_calendars(self):
        service = self.get_calendar_service()
        return iterate_google_list(service.calendarList())

    def create_calendar(self):
        service = self.get_calendar_service()
        calendar = {
            'summary': 'piprints calendar',
            'timeZone': 'Europe/Rome',
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        self.calendar_id = created_calendar['id']

        rule = dict(role='reader',scope=dict(type='default'))
        service.acl().insert(calendarId=self.calendar_id, body=rule).execute()
        
        return self.calendar_id

    def get_calendar(self):
        service = self.get_calendar_service()
        return service.calendars().get(calendarId=self.calendar_id).execute()
    
    def delete_calendar(self):
        service = self.get_calendar_service()
        service.calendars().delete(calendarId=self.calendar_id).execute()

    def iterate_calendar_events(self):
        service = self.get_calendar_service()
        return iterate_google_list(service.events(), calendarId=self.calendar_id)

    def get_calendar_event(self, event_id):
        service = self.get_calendar_service()
        return service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()

    def calendar_add_event(self, event_dict):
        """
        https://developers.google.com/google-apps/calendar/v3/reference/events
        """
        service = self.get_calendar_service()
        event = service.events().insert(calendarId=self.calendar_id, body=event_dict).execute()
        return event['id']

    def calendar_update_event(self, event_id, event_dict):
        service = self.get_calendar_service()
        service.events().update(calendarId=self.calendar_id, eventId=event_id, body=event_dict).execute()

    def calendar_delete_event(self, event_id):
        service = self.get_calendar_service()
        service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()

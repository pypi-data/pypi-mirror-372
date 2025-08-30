#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os, glob
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

import re

from datetime import date

from django.core.management import setup_environ
from . import settings
from django.core.files import File
from django.core.mail import send_mail, EmailMessage
from .main.models import *
from sys import stderr, stdout
from .settings import HOSTNAME, ROOT_URL, SERVER_EMAIL, ADMIN_EMAIL

setup_environ(settings)

def main():
    new_papers = Paper.objects.filter(notification_sent = False)
    if not new_papers:
        return
    print(('new papers:', new_papers))

    to = ADMIN_EMAIL
    subject = '[piprints News] New Papers'

    body = ''
    body += 'New papers were added to the piprints Preprint Server - http://%s\n' % HOSTNAME
    body += '\n'

    for paper in new_papers:
        body += 'title: %s\n' % paper.title
        body += 'authors: %s\n' % (', '.join(['%s %s' % (x.firstname,x.lastname) for x in paper.authors.all()]))
        body += 'reference: http://%s%s\n' % (HOSTNAME,paper.url())
        body += '\n'
        paper.notification_sent = True
        paper.save()

    print(("body: ", body))
    email = EmailMessage(
        subject = subject,
        body = body,
        from_email = SERVER_EMAIL,
        to = [to])

    email.send()
    
if __name__ == '__main__':
    main()



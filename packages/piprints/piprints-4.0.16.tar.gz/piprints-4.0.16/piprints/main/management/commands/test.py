import os

from django.core.management.base import BaseCommand, CommandError

from piprints.settings import BASE_ROOT

class Command(BaseCommand):
    help = 'run tests (with py.test instead of stanard django test)'

    def handle(self, *args, **options):
        os.chdir(BASE_ROOT)
        cmd = 'DJANGO_SETTINGS_MODULE=piprints.settings-test py.test'
        os.system(cmd)

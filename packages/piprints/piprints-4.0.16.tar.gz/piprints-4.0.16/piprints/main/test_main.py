import pytest
from pytest import mark 

from piprints.main.models import *
import piprints.settings

@pytest.fixture
def client():
    from django.test import Client
    return Client()

def test_messages(client):
    r = client.get('/test_messages')
    for word in ['success','info','warning','error']:
        assert word in r.content

def test_robots(client):
    r = client.get('/robots.txt')
    assert r.status_code == 200

@mark.django_db
def test_account_request(client):
    assert PersonRequest.objects.count() == 0
    r = client.get('/request/')
    post = {
        'lastname': 'Rossi',
        'firstname': 'Mario',
        'human': 'yes',
        }
    r = client.post('/request/',post)
    assert r.status_code == 200
    assert PersonRequest.objects.count() == 1

def test_bulletin():
    from django.core.management import call_command
    call_command('send_bulletin','email@some.org',dummy=True)
import os
import tempfile
import atexit
from base64 import b64encode

import pytest

from flask import g
from flask.testing import FlaskClient

from api import config

DBFD, DBPATH = tempfile.mkstemp()
atexit.register(os.remove, DBPATH)
os.close(DBFD)

# Settings under test.
config.DATABASE['name'] = DBPATH
config.TESTING = True

from api import urls
from api.app import db, app
from api.models import create_tables, drop_tables, User


class ConsoleClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self._global_headers = kwargs.pop('global_headers', None)
        super().__init__(*args, **kwargs)


    def open(self, *args, **kwargs):
        if self._global_headers:
            kwargs.setdefault('headers', {}).update(self._global_headers)
        return super().open(*args, **kwargs)


app.testing = True
app.test_client_class = ConsoleClient


@pytest.fixture(autouse=True)
def database():
    create_tables()
    user = User(pk=1, name='Test User', username='testuser')
    user.set_password('password')
    user.save()
    try:
        yield None

    finally:
        drop_tables()


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def session_auth():
    with app.test_client() as client:
        client.post('/api/users/login/', json={
            'username': 'testuser',
            'password': 'password',
        })
        try:
            yield client

        finally:
            client.post('/api/users/logout/')


@pytest.fixture
def basic_auth():
    with app.test_client(global_headers={
        'Authorization': b64encode('testuser:password'),
    }) as client:
        try:
            yield client

        finally:
            a.delete_instance()

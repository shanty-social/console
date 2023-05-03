import os
import tempfile
import atexit

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
from api.models import create_tables, drop_tables, User, Agent


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
def authenticated():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['authenticated'] = True
            session['user_pk'] = 1
        with app.app_context():
            g.user = User.select().where(User.id==1).get()
            try:
                yield client

            finally:
                g.user = None


@pytest.fixture
def agent():
    with app.test_client(global_headers={'Authorization': 'Bearer abc123'}) as client:
        with app.app_context():
            a = Agent.create(
                uuid='22a92175-d3aa-4d11-9a75-f19de56ef030',
                name='Test Agent',
                token='abc123',
                activated=True,
                remote_addr='127.0.0.1',
            )

        try:
            yield client

        finally:
            a.delete_instance()

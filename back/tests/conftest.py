import os
import tempfile
import atexit

import pytest

from flask import g

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

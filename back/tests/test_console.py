import os
import tempfile

import pytest

DBFD, os.environ['FLASK_DB_PATH'] = tempfile.mkstemp()

from api import app


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

    os.close(DBFD)
    os.unlink(os.environ['FLASK_DB_PATH'])


def test_foo(client):
    pass

import os
import time
import tempfile
import logging

import pytest

from api import config

DBFD, DBPATH = tempfile.mkstemp()
os.remove(DBPATH)
os.close(DBFD)

# Settings under test.
config.DATABASE['name'] = DBPATH
config.TESTING = True

from api import tasks
from api.tasks import CancelledError, TimeoutException
from api.app import app, create_tables


LOGGER = logging.getLogger()
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)


def _task_test(A, B, C=None):
    if C:
        # Hard sleep prevent cancellation & timeout.
        start = time.time()
        while time.time() - start < C:
            time.sleep(0.1)
    return A + B


@pytest.fixture
def client():
    create_tables()

    with app.test_client() as client:
        yield client


def test_task_wait(client):
    t = tasks.defer(_task_test, 1, 2)
    assert t.wait() == 3


def test_task_cancel(client):
    t = tasks.defer(_task_test, 1, 3, C=5.0)
    t.cancel()
    with pytest.raises(CancelledError):
        t.wait()


def test_task_timeout(client):
    t = tasks.defer(_task_test, 1, 3, C=5.0, timeout=1.0)
    with pytest.raises(TimeoutException):
        t.wait()

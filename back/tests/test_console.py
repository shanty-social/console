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

_CRON_TEST = {}


def _cron_test(*args, **kwargs):
    _CRON_TEST['A'] = 'I ran'


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
    "Ensure you can wait for a task result."
    t = tasks.defer(_task_test, args=(1, 2))
    assert t.wait() == 3


def test_task_cancel(client):
    "Ensure a task can be cancelled."
    t = tasks.defer(_task_test, args=(1, 3), kwargs={'C': 5.0})
    t.cancel()
    with pytest.raises(CancelledError):
        t.wait()


def test_task_timeout(client):
    "Ensure a task can timeout."
    t = tasks.defer(_task_test, args=(1, 3), kwargs={'C': 5.0}, timeout=1.0)
    with pytest.raises(TimeoutException):
        t.wait()


def test_cron(client):
    tasks.cron('* * * * *', 1, 4, C=5)(_cron_test)
    assert len(tasks.CRONTAB) == 1, 'Crontab did not schedule'
    tasks.start_scheduler(interval=0.1)
    time.sleep(0.2)
    assert _CRON_TEST['A'] == 'I ran', 'Cron task did not run'
    tasks.stop_scheduler()

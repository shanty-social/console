import time
import logging

import pytest

from api import tasks
from api.tasks import CancelledError, TimeoutException
from api.models import Task


LOGGER = logging.getLogger()
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)

_CRON_TEST = {}


def _cron_test(*args, **kwargs):
    "A task that has a side-effect our test can detect."
    _CRON_TEST['A'] = 'I ran'


def _task_test(A, B, C=None):
    "A task that can sleep and does some math."
    if C:
        # Hard sleep prevent cancellation & timeout.
        start = time.time()
        while time.time() - start < C:
            time.sleep(0.1)
    return A + B


def _task_log_test(A):
    "A generator task that emits log messages."
    for i in range(A):
        yield f'Log message: {i}'
    return A + 3


def test_task_wait():
    "Ensure you can wait for a task result."
    t = tasks.defer(_task_test, args=(1, 2))
    assert t.wait() == 3


def test_task_cancel():
    "Ensure a task can be cancelled."
    t = tasks.defer(_task_test, args=(1, 3), kwargs={'C': 5.0})
    t.cancel()
    with pytest.raises(CancelledError):
        t.wait()


def test_task_timeout():
    "Ensure a task can timeout."
    t = tasks.defer(_task_test, args=(1, 3), kwargs={'C': 5.0}, timeout=1.0)
    with pytest.raises(TimeoutException):
        t.wait()


def test_task_log():
    "Ensure a generator emits logs."
    t = tasks.defer(_task_log_test, args=(4,))
    assert t.wait() == 7, 'Invalid return value'
    t = t.refresh()
    assert t.tail.message == 'Log message: 3', 'Last log message is incorrect'
    for i, log in enumerate(t.log):
        assert log.message.endswith(str(i)), 'Log messages mismatch'


def test_cron():
    "Test task scheduling."
    crons = len(tasks.CRONTAB)
    tasks.cron('* * * * *', 1, 4, C=5)(_cron_test)
    assert len(tasks.CRONTAB) == crons + 1, 'Crontab did not schedule'
    tasks.start_background_tasks()
    time.sleep(0.1)
    assert _CRON_TEST['A'] == 'I ran', 'Cron task did not run'


def test_task_exception(authenticated):
    t = Task.create(function=test_task_exception, result=Exception('BOOM'))
    r = authenticated.get('/api/tasks/')
    assert r.status_code == 200, 'Invalid status code'

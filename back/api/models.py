import threading
import logging

from datetime import datetime

from peewee import (
    CharField, DateTimeField, ForeignKeyField, DeferredForeignKey,
    BigIntegerField,
)
from playhouse.fields import PickleField
from stopit import async_raise

from api.app import db


LOGGER = logging.getLogger()
LOGGER.addHandler(logging.NullHandler())


class UpperCharField(CharField):
    "Custom field to ensure values are upppercase"
    def python_value(self, val):
        return val.upper()

    def db_value(self, val):
        return val.upper()


class Setting(db.Model):
    "Store settings"
    name = UpperCharField(unique=True)
    value = PickleField(null=False)

    def __unicode__(self):
        return f'{self.name}={self.value}'


class Task(db.Model):
    "Background task"
    function = PickleField()
    args = PickleField(null=True)
    kwargs = PickleField(null=True)
    result = PickleField(null=True)
    ident = BigIntegerField(null=True)
    created = DateTimeField(default=datetime.now)
    completed = DateTimeField(default=None, null=True)
    tail = DeferredForeignKey('TaskLog', backref='tail_of', null=True)

    def get_result(self):
        # Get a fresh instance:
        task = self.refresh()
        if task.result is None:
            raise ValueError('Task not completed')
        if isinstance(task.result, Exception):
            raise task.result
        return task.result

    def cancel(self):
        if self.ident is None:
            raise ValueError('No thread identity')
        from api.tasks import CancelledError
        LOGGER.debug('Task[%i] Cancelling')
        async_raise(self.ident, CancelledError)

    def wait(self, timeout=None):
        LOGGER.debug('Task[%i] waiting, ident: %s', self.id, self.ident)
        for t in threading.enumerate():
            LOGGER.debug('Comparing %s == %s', t.ident, self.ident)
            if t.ident == self.ident:
                LOGGER.debug('Task[%i] found ident: %s', self.id, self.ident)
                break
        else:
            LOGGER.debug('Task[%i] ident not found: %s', self.id, self.ident)
            # Already done?
            return self.get_result()
        # Still running, wait...
        t.join(timeout=timeout)
        if t.is_alive():
            # if join() returns and thread is alive, we timed out.
            raise TimeoutError('Timed out waiting for thread')
        return self.get_result()

    def refresh(self):
        return type(self).get(self._pk_expr())


class TaskLog(db.Model):
    "Background task log output"
    task = ForeignKeyField(Task, backref='log')
    created = DateTimeField(default=datetime.now)
    message = CharField()

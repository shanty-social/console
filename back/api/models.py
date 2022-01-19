import threading
import logging
from uuid import uuid4

from datetime import datetime

from pkg_resources import parse_version
from restless.utils import json, MoreTypesJSONEncoder
from peewee import (
    CharField, DateTimeField, ForeignKeyField, DeferredForeignKey,
    BigIntegerField, TextField, BooleanField, UUIDField,
)
from playhouse.fields import PickleField
from stopit import async_raise

from api.app import db


LOGGER = logging.getLogger()
LOGGER.addHandler(logging.NullHandler())


def create_tables():
    "Create database tables."
    import api.models
    models = [
        m for m in api.models.__dict__.values() \
            if isinstance(m, type) and issubclass(m, db.Model)
    ]
    db.database.create_tables(models, safe=True)


def drop_tables():
    "Drop database tables (used between tests)."
    import api.models
    models = [
        m for m in api.models.__dict__.values() \
            if isinstance(m, type) and issubclass(m, db.Model)
    ]
    db.database.drop_tables(models, safe=True)


class UpperCharField(CharField):
    "Custom field to ensure values are upppercase."
    def python_value(self, val):
        return val.upper()

    def db_value(self, val):
        return val.upper()


class JSONField(TextField):
    "Custom field to store JSON."
    def python_value(self, val):
        return json.loads(val)

    def db_value(self, val):
        return json.dumps(data, cls=MoreTypesJSONEncoder)


class VersionField(CharField):
    "Custom field to store version strings."
    def python_value(self, val):
        return parse_version(val)

    def db_value(self, val):
        return str(val)
    

class Setting(db.Model):
    "Store settings."
    group = CharField(default='default')
    name = UpperCharField(unique=True)
    value = PickleField(null=False)

    def __unicode__(self):
        return f'<Setting {self.group}[{self.name}]={self.value}>'


class Task(db.Model):
    "Background task."
    id = UUIDField(primary_key=True, default=uuid4)
    function = PickleField()
    args = PickleField(null=True)
    kwargs = PickleField(null=True)
    result = PickleField(null=True)
    created = DateTimeField(default=datetime.now)
    completed = DateTimeField(default=None, null=True)
    tail = DeferredForeignKey('TaskLog', backref='tail_of', null=True)

    def __unicode__(self):
        return f'<Task {self.id}, {self.function.__name__}, ' \
               f'args={self.args}, kwargs={self.kwargs}>'

    def get_result(self):
        # Get a fresh instance:
        task = self.refresh()
        if task.result is None:
            raise ValueError('Task not completed')
        if isinstance(task.result, Exception):
            raise task.result
        return task.result

    def cancel(self):
        from api.tasks import CancelledError, find_thread
        LOGGER.debug('Task[%s] Cancelling', self.id)
        t = find_thread(str(self.id))
        async_raise(t.ident, CancelledError)

    def wait(self, timeout=None):
        from api.tasks import find_thread
        LOGGER.debug('Task[%s] waiting', self.id)
        t = find_thread(str(self.id))
        if t is None:
            LOGGER.debug('Task[%s] not found', self.id)
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
    "Background task log output."
    task = ForeignKeyField(Task, backref='log')
    created = DateTimeField(default=datetime.now)
    message = CharField()

    def __unicode__(self):
        return f'<TaskLog {self.message}>'


class Service(db.Model):
    "Services the user has chosen to deploy."
    uuid = UUIDField(primary_key=True)
    name = CharField()
    group = CharField(default='default')
    icon = CharField(null=True)
    description = TextField(null=True)
    version = CharField(null=False)
    enabled = BooleanField(default=True)
    meta = JSONField(null=False)

    def __unicode__(self):
        return f'<Service name={self.name}>'

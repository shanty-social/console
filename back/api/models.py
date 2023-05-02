import logging
from urllib.parse import urlparse, urlunparse, ParseResult
from uuid import uuid4

from datetime import datetime

from pkg_resources import parse_version
from restless.utils import json, MoreTypesJSONEncoder
from peewee import (
    CharField, DateTimeField, ForeignKeyField, DeferredForeignKey,
    TextField, BooleanField, UUIDField, SmallIntegerField,
)
from flask_peewee.utils import make_password, check_password
from playhouse.fields import PickleField
from playhouse.signals import (
    pre_save, post_save, pre_delete, post_delete, pre_init,
)
from stopit import async_raise

from api.app import db, socketio


LOGGER = logging.getLogger()
LOGGER.addHandler(logging.NullHandler())

DEFAULT_SETTING_GROUP = 'default'


def _get_models():
    return [
        m for m in globals().values()
        if isinstance(m, type) and issubclass(m, db.Model)
    ]


def create_tables():
    "Create database tables."
    db.database.create_tables(_get_models(), safe=True)


def drop_tables():
    "Drop database tables (used between tests)."
    db.database.drop_tables(_get_models(), safe=True)


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
        return json.dumps(val, cls=MoreTypesJSONEncoder)


class VersionField(CharField):
    "Custom field to store version strings."
    def python_value(self, val):
        return parse_version(val)

    def db_value(self, val):
        return str(val)


class URLField(CharField):
    "Custom field to store url."
    def python_value(self, val):
        return urlparse(val)

    def db_value(self, val):
        if isinstance(val, str):
            urlparse(val)
            return val
        elif isinstance(val, ParseResult):
            return urlunparse(val)
        else:
            return str(val)


class SignalMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pre_init.send(self)

    def save(self, *args, **kwargs):
        pk_value = self._pk if self._meta.primary_key else True
        created = kwargs.get('force_insert', False) or not bool(pk_value)
        pre_save.send(self, created=created)
        ret = super().save(*args, **kwargs)
        post_save.send(self, created=created)
        return ret

    def delete_instance(self, *args, **kwargs):
        pre_delete.send(self)
        ret = super().delete_instance(*args, **kwargs)
        post_delete.send(self)
        return ret


class Setting(db.Model):
    "Store settings."
    group = CharField(default=DEFAULT_SETTING_GROUP)
    name = UpperCharField(unique=True)
    value = PickleField(null=False)

    def __unicode__(self):
        return f'<Setting {self.group}[{self.name}]={self.value}>'

    @staticmethod
    def get_setting(name, group=DEFAULT_SETTING_GROUP):
        setting = Setting \
            .select() \
            .where(Setting.name == name, Setting.group == group) \
            .get()
        return setting.value

    def set_setting(name, value, group=DEFAULT_SETTING_GROUP):
        setting, created = Setting.get_or_create(
            name=name, defaults={'value': value})
        if not created:
            setting.value = value
            setting.save()


class Task(SignalMixin, db.Model):
    "Background task."
    class Meta:
        only_save_dirty = True

    id = UUIDField(primary_key=True, default=uuid4)
    function = PickleField(null=False)
    args = PickleField(null=True)
    kwargs = PickleField(null=True)
    result = PickleField(null=True)
    created = DateTimeField(default=datetime.now)
    completed = DateTimeField(default=None, null=True)
    tail = DeferredForeignKey('TaskLog', backref='tail_of', null=True)

    def __unicode__(self):
        return f'<Task {self.id}, {self.function.__name__}, ' \
               f'args={self.args}, kwargs={self.kwargs}>'

    def get_result(self, default=None):
        # Get a fresh instance:
        task = self.refresh()
        if task.completed is None:
            return default
        if isinstance(task.result, Exception):
            raise task.result
        return task.result

    def cancel(self, timeout=None):
        from api.tasks import CancelledError, find_thread
        LOGGER.debug('Task[%s] Cancelling', self.id)
        t = find_thread(str(self.id))
        if t is None:
            return
        try:
            async_raise(t.ident, CancelledError)
        except ValueError:
            return
        t.join(timeout=timeout)

    def delete_instance(self, *args, **kwargs):
        self.cancel()
        super().delete_instance(*args, **kwargs)

    def wait(self, timeout=None):
        from api.tasks import find_thread
        LOGGER.debug('Task[%s] waiting', self.id)
        t = find_thread(str(self.id))
        if t is not None:
            # Still running, wait...
            t.join(timeout=timeout)
            if t.is_alive():
                # if join() returns and thread is alive, we timed out.
                raise TimeoutError('Timed out waiting for thread')
        else:
            LOGGER.debug('Task[%s] not found', self.id)
        return self.get_result()

    def refresh(self):
        return type(self).get(self._pk_expr())

    def logger(self, message):
        LOGGER.debug('%s.log: %s', self, message)
        try:
            self.tail = TaskLog.create(task=self, message=message)
            self.save()

        except Exception:
            LOGGER.exception()


class TaskLog(db.Model):
    "Background task log output."
    task = ForeignKeyField(Task, backref='log')
    created = DateTimeField(default=datetime.now)
    message = PickleField()

    def __unicode__(self):
        return f'<TaskLog {self.message}>'


class User(db.Model):
    "User model for local authentication."
    username = CharField(null=False, unique=True)
    password = CharField(null=False)
    name = CharField(null=True)
    active = BooleanField(default=True)
    admin = BooleanField(default=False)

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)


class OAuthClient(db.Model):
    "OAuth authorizations"
    name = CharField(null=False, unique=True)
    token = JSONField(null=False)
    user = JSONField(null=False)


class Backend(SignalMixin, db.Model):
    "Backend which serves up a web application."
    name = CharField(null=False)
    url = URLField(null=False, unique=True)
    host = CharField(null=False)


class Frontend(SignalMixin, db.Model):
    "Frontend that accepts traffic from users."
    type = SmallIntegerField(choices=[
        (1, 'direct'),
        (2, 'tunnel'),
        (3, 'onion'),
    ])
    backend = ForeignKeyField(Backend, backref='frontends')
    url = URLField(null=False, unique=True)


class Message(SignalMixin, db.Model):
    "Message to user"
    subject = CharField(null=False)
    body = TextField(null=False)
    read = BooleanField(default=False)
    created = DateTimeField(default=datetime.now)

    @staticmethod
    def send(subject=None, body=None):
        return Message.create(subject=subject, body=body)


@post_save(sender=Task)
def on_task_save(sender, instance, created):
    "Publish task events to socket.io."
    from api.views.tasks import task_preparer
    socketio.emit('models.task.post_save',
                  task_preparer.prepare(instance.refresh()))


@post_delete(sender=Task)
def on_task_delete(sender, instance):
    "Publish task events to socket.io."
    from api.views.tasks import task_preparer
    socketio.emit('models.task.post_delete',
                  task_preparer.prepare(instance))


@post_save(sender=Message)
def on_message_save(sender, instance, created):
    "Publish task events to socket.io."
    from api.views.messages import message_preparer
    socketio.emit('models.message.post_save',
                  message_preparer.prepare(instance))


@post_save(sender=Backend)
def on_backend_save(sender, instance, created):
    "Publish backend events to socket.io."
    from api.views.backends import backend_preparer
    socketio.emit('models.backend.post_save',
                  backend_preparer.prepare(instance))


@post_delete(sender=Backend)
def on_backend_delete(sender, instance):
    "Publish backend events to socket.io."
    from api.views.backends import backend_preparer
    socketio.emit('models.backend.post_delete',
                  backend_preparer.prepare(instance))


@post_save(sender=Frontend)
def on_frontend_save(sender, instance, created):
    "Publish backend events to socket.io."
    from api.views.backends import backend_preparer
    socketio.emit('models.backend.post_save',
                  backend_preparer.prepare(instance))


@post_delete(sender=Frontend)
def on_frontend_delete(sender, instance):
    "Publish frontend events to socket.io."
    from api.views.frontends import frontend_preparer
    socketio.emit('models.frontend.post_delete',
                  frontend_preparer.prepare(instance))

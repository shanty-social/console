import logging
from uuid import uuid4

from datetime import datetime

from pkg_resources import parse_version
from restless.utils import json, MoreTypesJSONEncoder
from peewee import (
    CharField, DateTimeField, ForeignKeyField, DeferredForeignKey,
    TextField, BooleanField, UUIDField, IntegerField,
)
from flask_peewee.utils import make_password, check_password
from playhouse.fields import PickleField
from playhouse.signals import Signal, pre_save, post_save, pre_delete, post_delete, pre_init
from stopit import async_raise

from api.app import db, socketio


LOGGER = logging.getLogger()
LOGGER.addHandler(logging.NullHandler())

DEFAULT_SETTING_GROUP = 'default'
ENDPOINT_TYPES = {
    'direct': 'direct',
    'tunnel': 'tunnel',
}
DNS_TYPES = {
    'static': 'static',
    'dynamic': 'dynamic',
}
DNS_PROVIDERS = {
    'afraid': {
        'url': 'http://freedns.afraid.org',
        'options': ['User', 'Password'],
        'description': 'Free DNS Hosting, Dynamic DNS Hosting, Static DNS Hosting, subdomain and domain hosting.',
        'nameservers': 'ns1.afraid.org,ns2.afraid.org,ns3.afraid.org,ns4.afraid.org',
    },
    'cloudflare': {
        'url': 'https://www.cloudflare.com',
        'options': ['API_Token', 'Email', 'Zone'],
        'description': 'Cloudflare DNS is an enterprise-grade authoritative DNS service that offers the fastest response time, unparalleled redundancy, and advanced security with built-in DDoS mitigation and DNSSEC.',
    },
    'hurricane': {
        'url': 'https://dns.he.net',
        'options': ['Password'],
        'description': 'Hurricane Electric Free DNS Hosting portal. This tool will allow you to easily manage and maintain your forward and reverse DNS.',
    },
    'strato': {
        'url': 'https://www.strato.com',
        'options': ['User', 'Password'],
        'description': 'STRATO is the reliable web hosting provider for anyone seeking online success. We make web hosting fair and simple – at an unbeatable price and without unnecessary frills.',
        'nameservers': 'ns1.strato.de,ns2.strato.de,ns4.strato.de',
    },
}


def _get_models():
    # TODO: can I use globals() or something else here?
    import api.models
    return [
        m for m in api.models.__dict__.values()
        if isinstance(m, type) and issubclass(m, db.Model)
    ]


def create_tables():
    "Create database tables."
    db.database.create_tables(_get_models(), safe=True)
    uuid, created = Setting.get_or_create(
        name='CONSOLE_UUID', defaults={'value': str(uuid4())})


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
        async_raise(t.ident, CancelledError)
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


class Domain(db.Model):
    "Domain model representing dns domain."
    name = CharField(null=False, unique=True)
    type = CharField(null=False, choices=DNS_TYPES.items())
    provider = CharField(
        null=False, choices=[
            (name, name) for name in DNS_PROVIDERS.keys()
        ])
    options = JSONField()
    created = DateTimeField(default=datetime.now)

    @staticmethod
    def get_available_options(type, provider):
        # NOTE: Make a copy, otherwise "ip address" is appended.
        options = list(DNS_PROVIDERS.get(provider, {}).get('options', []))
        if type == 'static':
            options.append('ip address')
        return options


class Endpoint(db.Model):
    "Endpoint model representing traffic routing."
    class Meta:
        indexes = [
            (('path', 'domain'), True),
        ]

    name = CharField(null=False, unique=True)
    host = CharField(null=False)
    http_port_external = IntegerField(null=True)
    http_port_internal = IntegerField(null=True)
    https_port_external = IntegerField(null=True)
    https_port_internal = IntegerField(null=True)
    path = CharField(null=False, default='/')
    type = CharField(null=False, choices=ENDPOINT_TYPES.items())
    domain = ForeignKeyField(Domain, null=False, backref='entrypoints')
    created = DateTimeField(default=datetime.now)


class Torkey(db.Model):
    "Tor key representing key pair and resulting hostname (prefix denotes vanity address)."
    prefix = CharField(null=True)
    hostname = CharField(null=False, unique=True)
    public = CharField(null=False)
    secret = CharField(null=False)
    created = DateTimeField(default=datetime.now)


class Message(SignalMixin, db.Model):
    "Message to user"
    subject = CharField(null=False)
    body = TextField(null=False)
    read = BooleanField(default=False)
    created = DateTimeField(default=datetime.now)


@post_save(sender=Task)
def on_task_event(sender, instance, created):
    "Publish task events to socket.io."
    from api.views.tasks import task_preparer
    socketio.emit('models.task.post_save',
        task_preparer.prepare(instance.refresh()), broadcast=True)


@post_save(sender=Message)
def on_task_event(sender, instance, created):
    "Publish task events to socket.io."
    from api.views.messages import message_preparer
    socketio.emit('models.message.post_save',
        message_preparer.prepare(instance), broadcast=True)

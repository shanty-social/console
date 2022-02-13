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
from stopit import async_raise

from api.app import db


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
        'nameservers': 'ns1.afraid.org,ns2.afraid.org,ns3.afraid.org,ns4.afraid.org',
    },
    'cloudflare': {
        'url': 'https://www.cloudflare.com',
        'options': ['API_Token', 'Email', 'Zone'],
    },
    'hurricane': {
        'url': 'https://dns.he.net',
        'options': ['Password'],
    },
    'strato': {
        'url': 'https://www.strato.com',
        'options': ['User', 'Password'],
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
    User.get_or_create(
        username='admin',
        defaults={'name': 'Admin', 'password': make_password('password')}
    )
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


class Task(db.Model):
    "Background task."
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


class User(db.Model):
    "User model for local authentication."
    username = CharField(null=False, unique=True)
    password = CharField(null=False)
    name = CharField(null=True)
    active = BooleanField(default=True)

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)


class Domain(db.Model):
    "Domain model representing dns domain."
    name = CharField(null=False, unique=True)
    type = CharField(null=False, choices=DNS_TYPES.items())
    provider = CharField(
        null=False, choices=[
            (name, name) for name in DNS_PROVIDERS.keys()
        ])
    options = JSONField()

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

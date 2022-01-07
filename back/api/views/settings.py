import logging

from restless.preparers import FieldsPreparer
from restless.serializers import Serializer
from restless.utils import json, MoreTypesJSONEncoder
from flask import request
from flask_peewee.utils import get_object_or_404

from api.models import Setting
from api.views import BaseResource


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def to_text(settings):
    def _to_text(o):
        return f'{o["name"]}={o["value"]}'

    if 'objects' in settings:
        lines = []
        for setting in settings['objects']:
            lines.append(_to_text(setting))
        return '\n'.join(lines)

    else:
        return _to_text(settings)


def from_text(text):
    def _from_text(s):
        name, value = s.split('=')
        name = name.upper()
        return name, value

    settings = {}
    if '\n' in text:
        lines = settings['objects'] = []
        for line in text.splitlines():
            name, value = _from_text(line)
            lines.append({
                'name': name,
                'value': value,
            })

    else:
        name, value = _from_text(text)
        settings['name'] = name
        settings['value'] = value

    return settings


class TextOrJSONSerializer(Serializer):
    def deserialize(self, body):
        # This is Django-specific, but all frameworks can handle GET
        # parameters...
        ct = request.args.get('format', 'json')

        if ct == 'text':
            return from_text(body)
        else:
            return json.loads(body)

    def serialize(self, data):
        # Again, Django-specific.
        ct = request.args.get('format', 'json')

        if ct == 'text':
            return to_text(data)
        else:
            return json.dumps(data, cls=MoreTypesJSONEncoder)


class SettingResource(BaseResource):
    "Manage settings."
    preparer = FieldsPreparer(fields={
        'group': 'group',
        'name': 'name',
        'value': 'value',
    })
    serializer = TextOrJSONSerializer()

    def list(self):
        "List all settings."
        group = request.args.get('group')
        query = Setting.select()
        if group:
            query = query.where(Setting.group == group)
        return query

    def detail(self, pk):
        "Retrieve single setting."
        return get_object_or_404(Setting, Setting.name == pk)

    def create(self):
        "Create a new setting."
        setting = Setting(**self.data)
        setting.save()
        return setting

    def create_detail(self, pk):
        "Create single setting."
        setting = Setting(name=pk.upper(), **self.data)
        setting.save()
        return setting

    def update(self, pk):
        "Update single setting."
        setting = Setting.get(Setting.name == pk)
        setting.group = self.data.get('group')
        setting.value = self.data.get('value')
        return setting

    def delete(self, pk):
        "Delete settings."
        Setting.delete().where(Setting.name == pk)

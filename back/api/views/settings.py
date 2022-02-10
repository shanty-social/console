import logging

from restless.preparers import FieldsPreparer
from flask import request, abort
from flask_peewee.utils import get_object_or_404

from api.models import Setting
from api.views import BaseResource, TextOrJSONSerializer


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


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
        "Create new setting(s)."
        try:
            name = self.data['name'].upper()
            value = self.data['value']
        except KeyError:
            abort(400)
        setting, created = Setting.get_or_create(
            name=name, defaults={'value': value})
        if not created:
            setting.value = value
            setting.save()
        return setting

    def create_detail(self, pk):
        "Create single setting."
        try:
            value = self.data['value']
        except KeyError:
            abort(400)
        setting, created = Setting.get_or_create(
            name=pk.upper(), defaults={'value': value})
        if not created:
            setting.value = value
            setting.save()
        return setting

    def update(self, pk):
        "Update single setting."
        setting = get_object_or_404(Setting, Setting.name == pk)
        setting.group = self.data.get('group')
        setting.value = self.data.get('value')
        setting.save()
        return setting

    def delete(self, pk):
        "Delete single setting."
        setting = get_object_or_404(Setting, Setting.name == pk)
        setting.delete_instance()

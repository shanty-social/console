import logging

from restless.preparers import FieldsPreparer
from flask import request
from flask_peewee.utils import get_object_or_404

from api.models import Setting
from api.views import BaseResource


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class SettingResource(BaseResource):
    "Manage settings."
    preparer = FieldsPreparer(fields={
        'group': 'group',
        'name': 'name',
        'value': 'value',
    })

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

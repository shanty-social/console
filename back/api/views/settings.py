import logging

from restless.preparers import FieldsPreparer
from flask import request
from flask_peewee.utils import get_object_or_404

from wtfpeewee.orm import model_form

from api.models import Setting
from api.views import (
    BaseResource, MultiSerializer, JSONSerializer, TextSerializer, Form,
    abort,
)


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

SettingForm = model_form(Setting, base_class=Form)


class SettingSerializer(TextSerializer):
    def serialize(self, body):
        if 'name' in body and 'value' in body:
            body = {body['name']: body['value']}

        elif 'objects' in body:
            body = {
                o['name']: o['value'] for o in body['objects']
            }

        return super().serialize(body)

    def deserialize(self, body):
        obj = super().deserialize(body)
        if len(obj) == 1:
            n, v = list(obj.items())[0]
            return {
                'name': n,
                'value': v
            }

        else:
            return [
                {'name': n, 'value': v} for n, v in obj.items()
            ]


class SettingResource(BaseResource):
    "Manage settings."
    preparer = FieldsPreparer(fields={
        'group': 'group',
        'name': 'name',
        'value': 'value',
    })
    serializer = MultiSerializer(
        json=JSONSerializer(), text=SettingSerializer())

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
        form = SettingForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        setting, created = Setting.get_or_create(
            name=form.name.data.upper(), defaults={'value': form.value.data})
        if not created:
            form.populate_obj(setting)
            setting.save()
        return setting

    def create_detail(self, pk):
        "Create single setting."
        form = SettingForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        setting, created = Setting.get_or_create(
            name=pk.upper(), defaults={'value': form.value.data})
        if not created:
            form.populate_obj(setting)
            setting.save()
        return setting

    def update(self, pk):
        "Update single setting."
        setting = get_object_or_404(Setting, Setting.name == pk)
        form = SettingForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        form.populate_obj(setting)
        setting.save()
        return setting

    def delete(self, pk):
        "Delete single setting."
        setting = get_object_or_404(Setting, Setting.name == pk)
        setting.delete_instance()

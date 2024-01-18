import logging

from flask import request
from flask_peewee.utils import get_object_or_404
from restless.preparers import FieldsPreparer

from wtfpeewee.orm import model_form
from wtforms.validators import DataRequired

from api.models import Network
from api.views import BaseResource, Form, abort, DependsOn


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


NetworkFormBase = model_form(Network, base_class=Form)


class NetworkForm(NetworkFormBase):
    def validate(self):
        extra_validators = {
            'address': DependsOn('dhcp', False),
            'netmask': DependsOn('dhcp', False),
            'gateway': DependsOn('dhcp', False),
            'ssid': DependsOn('type', 'wifi'),
            'wpa': DependsOn('type', 'wifi'),
        }
        return super().validate(extra_validators)


network_preparer = FieldsPreparer(fields={
    'id': 'id',
    'name': 'name',
    'address': 'address',
    'netmask': 'netmask',
    'gateway': 'gateway',
    'dhcp': 'dhcp',
    'ssid': 'ssid',
    'wpa': 'wpa',
    'type': 'type',
    'enabled': 'enabled',
    'status': 'status',
})


class NetworkResource(BaseResource):
    "Manage network interfaces."
    preparer = network_preparer

    def list(self):
        "List all interfaces."
        return Network.select()

    def detail(self, pk):
        "Retrieve single interface."
        return get_object_or_404(Network, Network.id == pk)

    def create(self):
        "Create new interface."
        form = NetworkForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        interface = Network.create({
            'subject': form.subject.data,
            'body': form.body.data,
        })
        return interface

    def delete(self, pk):
        "Delete interface."
        interface = get_object_or_404(Network, Network.id == pk)
        interface.delete_instance()

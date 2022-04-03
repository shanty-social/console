import logging

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer

from wtfpeewee.orm import model_form

from api.views import BaseResource, Form, abort
from api.models import Endpoint


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


EndpointForm = model_form(Endpoint, base_class=Form)


class EndpointResource(BaseResource):
    "Manage Endpoints."
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'host': 'host',
        'port': 'port',
        'path': 'path',
        'domain_name': 'domain_name',
    })

    def list(self):
        "List all endpoints."
        type = request.args.get('type')
        domain_name = request.args.get('domain_name')
        host = request.args.get('host')
        endpoints = Endpoint.select()
        if type:
            endpoints = endpoints.where(Endpoint.type == type)
        if domain_name:
            endpoints = endpoints.where(Endpoint.type == domain_name)
        if host:
            endpoints = endpoints.where(Endpoint.host == host)
        return endpoints

    def detail(self, pk):
        "Retrieve single endpoint."
        return get_object_or_404(Endpoint, Endpoint.name == pk)

    def create(self):
        "Create new endpoint(s)."
        form = EndpointForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        endpoint, created = Endpoint.get_or_create(
            name=form.name.data, defaults={
                'host': form.host.data,
                'port': form.port.data,
                'path': form.path.data,
                'domain_name': form.domain_name.data,
            }
        )
        if not created:
            form.populate_obj(endpoint)
            endpoint.save()
        return endpoint

    def update(self, pk):
        "Update single endpoint."
        endpoint = get_object_or_404(Endpoint, Endpoint.name == pk)
        form = EndpointForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        form.populate_obj(endpoint)
        endpoint.save()
        return endpoint

    def delete(self, pk):
        "Delete single endpoint."
        endpoint = get_object_or_404(Endpoint, Endpoint.name == pk)
        endpoint.delete_instance()

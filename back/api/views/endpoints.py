import logging

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer, SubPreparer

from wtfpeewee.orm import model_form

from api.views import BaseResource, Form, abort
from api.models import Endpoint, Domain


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


EndpointForm = model_form(Endpoint, base_class=Form)


domain_preparer = FieldsPreparer(fields={
    'name': 'name',
    'provider': 'provider',
})


class EndpointResource(BaseResource):
    "Manage Endpoints."
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'host': 'host',
        'http_port_external': 'http_port_external',
        'http_port_internal': 'http_port_internal',
        'https_port_external': 'https_port_external',
        'https_port_internal': 'https_port_internal',
        'path': 'path',
        'type': 'type',
        'domain': SubPreparer('domain', domain_preparer),
    })

    def list(self):
        "List all endpoints."
        type = request.args.get('type')
        domain_name = request.args.get('domain')
        host = request.args.get('host')
        endpoints = Endpoint.select()
        if type:
            endpoints = endpoints.where(Endpoint.type == type)
        if domain_name:
            endpoints = endpoints.join(Domain) \
                                 .where(Domain.name == domain_name)
        if host:
            endpoints = endpoints.where(Endpoint.host == host)
        return endpoints

    def detail(self, pk):
        "Retrieve single endpoint."
        return get_object_or_404(Endpoint, Endpoint.name == pk)

    def create(self):
        "Create new endpoint(s)."
        self.data['domain'] = get_object_or_404(
            Domain, Domain.name == self.data.get('domain'))
        form = EndpointForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        endpoint, created = Endpoint.get_or_create(
            name=form.name.data, defaults={
                'host': form.host.data,
                'http_port_external': form.http_port_external.data,
                'http_port_internal': form.http_port_internal.data,
                'https_port_external': form.https_port_external.data,
                'https_port_internal': form.https_port_internal.data,
                'path': form.path.data,
                'type': form.type.data,
                'domain': form.domain.data,
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
        if form.domain.data:
            endpoint.domain = Domain.get(Domain.name == form.domain.data)
        endpoint.save()
        return endpoint

    def delete(self, pk):
        "Delete single endpoint."
        endpoint = get_object_or_404(Endpoint, Endpoint.name == pk)
        endpoint.delete_instance()

import logging

from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer, SubPreparer

from wtfpeewee.orm import model_form

from api.views import BaseResource, TextOrJSONSerializer, Form, abort
from api.models import Endpoint, Domain
from api.tasks import cron
from api.views.ports import _open_port, _get_gateway


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


EndpointForm = model_form(Endpoint, base_class=Form)


@cron('*/5 * * * *')
def _check_endpoint_ports():
    try:
        gateway, service = _get_gateway()

    except Exception:
        LOGGER.exception('Error getting gateway')
        return

    for endpoint in Endpoint.select(Endpoint.type == 'direct'):
        if endpoint.http_port:
            _open_port(
                gateway, service, 80, endpoint.http_port, endpoint.host)
        if endpoint.https_port:
            _open_port(
                gateway, service, 443, endpoint.https_port, endpoint.host)


domain_preparer = FieldsPreparer(fields={
    'name': 'name',
    'provider': 'provider',
    'options': 'options',
})


class EndpointResource(BaseResource):
    "Manage Endpoints."
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'host': 'host',
        'http_port': 'http_port',
        'https_port': 'https_port',
        'path': 'path',
        'type': 'type',
        'domain': SubPreparer('domain', domain_preparer),
    })
    serializer = TextOrJSONSerializer()

    def list(self):
        "List all endpoints."
        return Endpoint.select()

    def detail(self, pk):
        "Retrieve single endpoint."
        return get_object_or_404(Endpoint, Endpoint.name == pk)

    def create(self):
        "Create new endpoint(s)."
        form = EndpointForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        domain = get_object_or_404(Domain, Domain.name == form.domain.data)
        endpoint, created = Endpoint.get_or_create(
            name=form.name.data, defaults={
                'host': form.host.data,
                'http_port': form.http_port.data,
                'https_port': form.https_port.data,
                'path': form.path.data,
                'type': form.type.data,
                'domain': domain,
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

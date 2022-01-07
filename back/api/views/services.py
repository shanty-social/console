import logging
import requests

from http import HTTPStatus

from restless.preparers import FieldsPreparer
from flask import request, redirect
from flask_peewee.utils import get_object_or_404

from api.app import cache
from api.models import Service
from api.views import BaseResource, to_bool
from api.external.docker import ServiceInfo
from api.tasks import cron, defer
from api.config import SERVICE_URL


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


@cron('0 */4 * * *')
def update_services():
    "Pull service information from website and update local data."
    if not SERVICE_URL:
        LOGGER.warning('Cannot update service descriptions, no URL')
        return

    data = requests.get(SERVICE_URL).json()
    for obj in data:
        try:
            service = Service.get(Service.name == obj['name'])

        except Service.DoesNotExist:
            service = Service(name=obj['name'])

        info = ServiceInfo.get()
        service.downloaded, service.installed_version = \
            info.get_installed_version(service.name)
        service.latest_version = obj['version']
        for attr in ('group', 'icon', 'description'):
            setattr(service, attr, obj[attr])

        service.save()

    data_names = [obj.name for obj in data]
    for service in Service.select():
        if service.name not in data_names:
            LOGGER.info('Purging service: %s', service.name)
            service.delete_instance()
            continue


def update_service(name, enabled=None, version=None):
    pass


def install_service(name, version=None):
    pass


def uninstall_service(name):
    pass


def refresh():
    "Refresh service registry."
    t = defer(update_services)
    return redirect(
        f'/api/tasks/{t.id}/', code=HTTPStatus.TEMPORARY_REDIRECT)


class ServiceResource(BaseResource):
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'group': 'group',
        'icon': 'icon',
        'description': 'description',
        'version': 'version',
        'enabled': 'enabled',
        'meta': 'meta'
    })

    def list(self):
        "List all available and installed services."
        group = request.args.get('group')
        query = Service.select()
        if group:
            query = query.where(Service.group == group)
        return query

    def detail(self, pk):
        "Details of a particular service."
        return get_object_or_404(Service, Service.name == pk)

    def create(self):
        "Install a service."
        try:
            name = self.data['name']
        except KeyError:
            abort(HTTPStatus.BAD_REQUEST)
        version = self.data.get('version')
        # TODO: validate service name.
        t = defer(install_service, args=(name,), kwargs={'version': version})
        return redirect(
            f'/api/tasks/{t.id}/', code=HTTPStatus.TEMPORARY_REDIRECT)

    def create_detail(self, pk):
        "Install a service."
        # TODO: validate service name.
        version = self.data.get('version')
        t = defer(install_service, args=(pk), kwargs={'version': version})
        return redirect(
            f'/api/tasks/{t.id}/', HTTPStatus.TEMPORARY_REDIRECT)

    def update(self, pk):
        "Disable or enable a service."
        service = get_object_or_404(Service, Service.name == pk)
        kwargs = {
            'enabled': to_bool(self.data.pop('enabled', None)),
            'version': self.data.pop('version', None),
        }

        if ((not any(map(lambda v: v is not None, kwargs.values())) or
             len(self.data) != 0)):
            # No other fields allowed.
            abort(HTTPStatus.BAD_REQUEST)

        t = defer(
            update_service, args=(service.name),
            kwargs=kwargs)
        return redirect(
            f'/api/tasks/{t.id}/', HTTPStatus.TEMPORARY_REDIRECT)

    def delete(self, pk):
        "Uninstall a service."
        service = get_object_or_404(Service, Service.name == pk)
        t = defer(uninstall_service, args=(service))
        return redirect(
            f'/api/tasks/{t.id}/', HTTPStatus.TEMPORARY_REDIRECT)

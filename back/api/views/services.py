import logging

from restless.preparers import FieldsPreparer
from flask import request
from flask_peewee.utils import get_object_or_404

from api.models import Service
from api.views import BaseResource
# from api.external.docker import ServiceInfo


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class ServiceResource(BaseResource):
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'group': 'group',
        'icon': 'icon',
        'description': 'description',
        'latest_version': 'latest_version',
        'installed_version': 'installed_version',
    })

    def list(self):
        group = request.args.get('group')
        query = Service.select()
        if group:
            query = query.where(Service.group == group)
        return query

    def detail(self, pk):
        return get_object_or_404(Service, Service.name == pk)

    def create(self):
        service = Service(**self.data)
        service.save()
        return service

    def create_detail(self, pk):
        service = Service(name=pk.upper(), **self.data)
        service.save()
        return service

    def update(self, pk):
        service = Service.get(Service.name == pk)
        service.group = self.data.get('group')
        service.value = self.data.get('value')
        return service

    def delete(self, pk):
        Service.delete().where(Service.name == pk)

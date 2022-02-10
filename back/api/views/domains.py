import logging

from flask import request, abort
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer

from api.views import BaseResource, TextOrJSONSerializer
from api.models import Domain


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class DomainResource(BaseResource):
    "Manage domains."
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'provider': 'provider',
        'options': 'options',
    })
    serializer = TextOrJSONSerializer()

    def list(self, pk):
        "List all domains."
        return Domain.select()

    def detail(self, pk):
        "Get single domain."
        return get_object_or_404(Setting, Setting.name == pk)

    def create(self):
        "Create new domain(s)."
        try:
            name = self.data['name']
            provider = self.data['provider']
            options = self.data['options']
        except KeyError:
            abort(400)
        missing = Domain.validate_options(provider, options)
        if missing:
            abort(400)
        domain, created = Domain.get_or_create(
            name=name, defaults={
                'provider': provider,
                'options': options
            })
        if not created:
            domain.provider = provider
            domain.options = options
            domain.save()
        return domain

    def create_detail(self, pk):
        "Create single domain."
        try:
            provider = self.data['provider']
            options = self.data['options']
        except KeyError:
            abort(400)
        missing = Domain.validate_options(provider, options)
        if missing:
            abort(400)
        domain, created = Domain.get_or_create(
            name=pk, defaults={
                'provider': provider,
                'options': options
            })
        if not created:
            domain.provider = provider
            domain.options = options
            domain.save()
        return domain

    def update(self, pk):
        "Update single domain."
        domain = get_object_or_404(Domain, Domain.name == pk)
        domain.group = self.data.get('group')
        domain.value = self.data.get('value')
        domain.save()
        return domain

    def delete(self, pk):
        "Delete single domain."
        domain = get_object_or_404(Domain, Domain.name == pk)
        domain.delete_instance()

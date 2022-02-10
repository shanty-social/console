import logging

from flask import abort, request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer
from restless.resources import skip_prepare

from api.views import BaseResource, TextOrJSONSerializer
from api.models import Domain, DNS_PROVIDERS


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_methods.update({
            'options': {
                'GET': 'options',
            },
            'providers': {
                'GET': 'providers',
            },
        })

    @classmethod
    def add_url_rules(cls, app, rule_prefix, endpoint_prefix=None):
        super().add_url_rules(app, rule_prefix, endpoint_prefix=endpoint_prefix)
        app.add_url_rule(
            rule_prefix + 'options/',
            endpoint=cls.build_endpoint_name('options', endpoint_prefix),
            view_func=cls.as_view('options'),
            methods=['GET']
        )
        app.add_url_rule(
            rule_prefix + 'providers/',
            endpoint=cls.build_endpoint_name('providers', endpoint_prefix),
            view_func=cls.as_view('providers'),
            methods=['GET']
        )

    def list(self):
        "List all domains."
        return Domain.select()

    def detail(self, pk):
        "Get single domain."
        return get_object_or_404(Domain, Domain.name == pk)

    def create(self):
        "Create new domain(s)."
        try:
            name = self.data['name']
            type = self.data['type']
            provider = self.data['provider']
            options = self.data['options']
        except KeyError:
            abort(400)
        for option in Domain.get_available_options(type, provider):
            if not options.get(option):
                abort(400)
        domain, created = Domain.get_or_create(
            name=name, defaults={
                'type': type,
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
            type = self.data['type']
            provider = self.data['provider']
            options = self.data['options']
        except KeyError:
            abort(400)
        for option in Domain.get_available_options(type, provider):
            if not options.get(option):
                abort(400)
        domain, created = Domain.get_or_create(
            name=pk, defaults={
                'type': type,
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
        domain.name = self.data.get('name')
        domain.type = type = self.data.get('type')
        domain.provider = provider = self.data.get('provider')
        domain.options = self.data.get('options')
        for option in Domain.get_available_options(type, provider):
            if not domain.options.get(option):
                abort(400)
        domain.save()
        return domain

    def delete(self, pk):
        "Delete single domain."
        domain = get_object_or_404(Domain, Domain.name == pk)
        domain.delete_instance()

    @skip_prepare
    def options(self):
        try:
            type = request.args['type']
            provider = request.args['provider']
        except KeyError:
            abort(400)
        return Domain.get_available_options(type, provider)

    @skip_prepare
    def providers(self):
        return DNS_PROVIDERS

import logging

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer
from restless.resources import skip_prepare

from wtfpeewee.orm import model_form

from api.app import oauth
from api.views import BaseResource, Form, abort
from api.models import Domain, DNS_PROVIDERS


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


DomainForm = model_form(Domain, base_class=Form)


class DomainResource(BaseResource):
    "Manage domains."
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'provider': 'provider',
        'options': 'options',
    })
    extra_actions = {
        'options': ['GET'],
        'providers': ['GET'],
        'shared': ['GET'],
        'check': ['POST'],
    }

    def list(self):
        "List all domains."
        provider = request.args.get('provider')
        domains = Domain.select()
        if provider:
            domains = domains.where(Domain.provider == provider)
        return domains

    def detail(self, pk):
        "Get single domain."
        return get_object_or_404(Domain, Domain.name == pk)

    def create(self):
        "Create new domain(s)."
        form = DomainForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        for option in Domain.get_available_options(form.type.data,
                                                   form.provider.data):
            if not form.options.data.get(option):
                abort(400, {f'options.{option}': 'required'})
        domain, created = Domain.get_or_create(
            name=form.name.data, defaults={
                'type': form.type.data,
                'provider': form.provider.data,
                'options': form.options.data
            })
        if not created:
            form.populate_obj(domain)
            domain.save()
        return domain

    def update(self, pk):
        "Update single domain."
        domain = get_object_or_404(Domain, Domain.name == pk)
        form = DomainForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        for option in Domain.get_available_options(form.type.data,
                                                   form.provider.data):
            if not form.options.data.get(option):
                abort(400, {f'options.{option}': 'required'})
        form.populate_obj(domain)
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

        except KeyError as e:
            abort(400, {e.args[0]: 'required'})
        return Domain.get_available_options(type, provider)

    @skip_prepare
    def providers(self):
        return DNS_PROVIDERS

    @skip_prepare
    def shared(self):
        r = oauth.shanty.get('/api/hosts/shared/')
        if r.status_code != 200:
            abort(r.status_code, {'message': r.reason})
        return r.json()

    @skip_prepare
    def check(self):
        name = self.data.get('name')
        if not name:
            abort(400, {'message': 'Invalid request'})
        r = oauth.shanty.post('/api/hosts/check/', data={'name': name})
        abort(r.status_code, {'message': r.reason})

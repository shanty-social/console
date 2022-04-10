from urllib.parse import urljoin

import requests

from restless.preparers import FieldsPreparer
from restless.resources import skip_prepare

from flask import session, request

from wtfpeewee.orm import model_form
from flask_peewee.utils import get_object_or_404

from api.app import oauth, update_token, delete_token
from api.tasks import cron
from api.views import (
    url_for, url_redir, Form, BaseResource, abort, RedirectResponse
)
from api import config
from api.models import OAuthClient


@cron('*/5 * * * *')
def refresh_tokens():
    "Refresh oauth tokens."


OAuthClientForm = model_form(OAuthClient, base_class=Form)


client_preparer = FieldsPreparer(fields={
    'name': 'name',
    'user': 'user',
})


class OAuthClientResource(BaseResource):
    "Manage OAuth Clients"
    preparer = client_preparer
    extra_actions = {
        'providers': ['GET'],
    }
    extra_details = {
        'start': ['GET'],
        'authorize': ['GET'],
        'domains': ['GET'],
        'check_domain': ['POST'],
    }

    def _get_service(self, name):
        try:
            return getattr(oauth, name)
        except AttributeError:
            abort(404)

    def is_authenticated(self):
        if self.endpoint in ('providers'):
            return True
        return super().is_authenticated()

    def list(self):
        return OAuthClient.select()

    def detail(self, pk):
        return get_object_or_404(OAuthClient, OAuthClient.name == pk)

    def delete(self, pk):
        client = get_object_or_404(OAuthClient, OAuthClient.name == pk)
        client.delete_instance()

    @skip_prepare
    def start(self, pk):
        next = request.args.get('next', '/#/settings')
        service = self._get_service(pk)
        if service.token:
            # Validate token.
            if service.get('/api/users/whoami/').status_code == 200:
                raise RedirectResponse(url_redir(next))
            # Delete invalid token.
            delete_token(pk)
        session['next'] = next
        redirect_uri = url_for(
            'api_oauthclient_authorize', pk=pk)
        r = service.authorize_redirect(redirect_uri, in_fragment=True)
        raise RedirectResponse(r.headers['Location'], code=r.status)

    def authorize(self, pk):
        next = url_redir(session.pop('next', '/#/settings'))
        service = self._get_service(pk)
        token = service.authorize_access_token()
        update_token('shanty', token, user=token.get('userinfo'))
        raise RedirectResponse(next)

    @skip_prepare
    def providers(self):
        providers = []
        for provider in config.OAUTH_PROVIDERS[:]:
            name = provider['name']
            base_url = getattr(config, f'{name.upper()}_BASE_URL')
            r = requests.get(urljoin(base_url, '/api/hosts/shared/'))
            provider['domains'] = r.json()
            providers.append(provider)
        return {'objects': providers}

    @skip_prepare
    def domains(self, pk):
        service = self._get_service(pk)
        r = service.get('/api/hosts/shared/')
        if r.status_code != 200:
            abort(r.status_code, {'message': r.reason})
        return r.json()

    @skip_prepare
    def check_domain(self, pk):
        service = self._get_service(pk)
        name = self.data.get('name')
        if not name:
            abort(400, {'message': 'Invalid request'})
        r = service.post('/api/hosts/check/', data={'name': name})
        abort(r.status_code, {'message': r.reason})

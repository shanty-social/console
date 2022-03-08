from flask import redirect, session, request, abort, jsonify, g

from api.app import oauth, update_token, delete_token
from api.auth import (
    requires_auth, log_in_user, log_out_user, get_logged_in_user,
)
from api.tasks import cron
from api.views import url_for, url_redir
from api.config import OAUTH_PROVIDERS
from api.models import Setting


@cron('*/5 * * * *')
def refresh_tokens():
    "Refresh oauth tokens."


def providers():
    return jsonify(OAUTH_PROVIDERS)


def whoami():
    return jsonify(get_logged_in_user())


def start(service_name):
    # Kick off OAuth2 authorization.
    next = url_redir(request.args.get('next', '/'))
    service = getattr(oauth, service_name, None)
    if service is None:
        abort(404)
    if service.token:
        # Validate token.
        r = oauth.shanty.get('/api/users/whoami/')
        if r.status_code == 200:
            return redirect(next)
        # Delete invalid token.
        delete_token(service_name)
    session['next'] = next
    redirect_uri = url_for(
        'authorize', service_name=service_name)
    return service.authorize_redirect(redirect_uri, in_fragment=True)


def authorize(service_name):
    # Return from OAuth2 Authorization
    next = session.pop('next', '/')
    service = getattr(oauth, service_name, None)
    if service is None:
        abort(404)
    token = service.authorize_access_token()
    update_token('shanty', token)
    # Get console token.
    r = service.post(
        '/api/consoles/', data={ 'uuid': Setting.get_setting('CONSOLE_UUID')})
    if r.status_code == 201:
        Setting.set_setting('CONSOLE_TOKEN', r.json().get('token'))
    log_in_user(token.get('userinfo'))
    return redirect(next)


def end(service_name):
    next = url_redir(request.args.get('next', '/'))
    delete_token(service_name)
    log_out_user()
    return redirect(next)

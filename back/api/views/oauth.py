from flask import url_for, redirect, session, request, abort

from api.app import oauth, update_token, delete_token
from api.auth import requires_auth


WHOAMI = '/api/users/whoami/'


@requires_auth()
def start(service_name):
    # Kick off OAuth2 authorization.
    next = request.args.get('next', '/')
    service = getattr(oauth, service_name, None)
    if service is None:
        abort(404)
    if service.token:
        # Validate token.
        r = oauth.shanty.get(WHOAMI)
        if r.status_code == 200:
            return redirect(next)
        # Delete invalid token.
        delete_token(service_name)
    session['next'] = next
    redirect_uri = url_for(
        'authorize',
        service_name=service_name,
        _external=True)
    return service.authorize_redirect(redirect_uri, in_fragment=True)


@requires_auth()
def authorize(service_name):
    # Return from OAuth2 Authorization
    next = session.pop('next', '/')
    service = getattr(oauth, service_name, None)
    if service is None:
        abort(404)
    update_token('shanty', service.authorize_access_token())
    # Test token.
    service.get(WHOAMI).json()
    return redirect(next)


@requires_auth()
def end(service_name):
    next = request.args.get('next', '/')
    delete_token(service_name)
    return redirect(next)

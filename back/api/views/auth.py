from restless.preparers import FieldsPreparer
from flask import g, url_for, redirect, session, request, abort

from api.app import oauth, update_token, delete_token
from api.auth import get_logged_in_user
from api.views import BaseResource
from api.models import User


WHOAMI = '/api/users/whoami/'


def oauth_start(service_name):
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
        'oauth_authorize',
        service_name=service_name,
        _external=True)
    return service.authorize_redirect(redirect_uri, in_fragment=True)


def oauth_authorize(service_name):
    # Return from OAuth2 Authorization
    next = session.pop('next', '/')
    service = getattr(oauth, service_name, None)
    if service is None:
        abort(404)
    update_token('shanty', service.authorize_access_token())
    # Test token.
    service.get(WHOAMI).json()
    return redirect(next)


def oauth_end(service_name):
    next = request.args.get('next', '/')
    delete_token(service_name)
    return redirect(next)


def login():
    next = request.args.get('next', '/')

    json = request.get_json()
    if json:
        username = json.get('username')
        password = json.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    if not username or not password:
        abort(400)

    try:
        user = User \
            .select() \
            .where(
                User.username == username,
                User.active == True  # noqa: E712
            ) \
            .get()

    except User.DoesNotExist:
        print(f'no user: {username}')
        abort(401)

    if not user.check_password(password):
        abort(401)

    session['authenticated'] = True
    session['user_pk'] = user._pk
    g.user = user

    return redirect(next)


def logout():
    next = request.args.get('next', '/')
    session.clear()
    g.user = None
    return redirect(next)


class WhoamiResource(BaseResource):
    preparer = FieldsPreparer(fields={
        'username': 'username',
        'name': 'name',
        'active': 'active',
    })

    def detail(self):
        "Details of a particular service."
        return get_logged_in_user()

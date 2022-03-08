from functools import wraps

from flask import session, request, abort

from api.app import app


def get_logged_in_user():
    "Get currently logged in user."
    if session.get('authenticated'):
        return session.get('user')


def log_in_user(userinfo):
    "Log user in."
    session['authenticated'] = True
    session['user'] = userinfo
    return userinfo


def log_out_user():
    "Log user out."
    session.clear()


def session_auth():
    "Check for user in session."
    return get_logged_in_user() is not None


def token_auth():
    "Check auth token in Authorization: header."
    token = app.config['AUTH_TOKEN']
    if not token:
        return
    authz = request.headers.get('authorization')
    if not authz:
        return
    if authz.startswith('Bearer '):
        authz = authz[7:]
    return authz == token


def requires_auth(auth_methods=[token_auth, session_auth]):
    """
    Decorator that requires one of our auth methods for a function based view.
    """
    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            for auth_method in auth_methods:
                if auth_method():
                    return f(*args, **kwargs)
            abort(401)

        return inner
    return wrapper

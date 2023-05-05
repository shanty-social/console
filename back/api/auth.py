import logging
from base64 import b64decode
from functools import wraps

from flask import g, session, abort, request

from api.models import User


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def get_logged_in_user():
    "Retrieves user from global or session.."
    if getattr(g, 'user', None):
        return g.user

    if session.get('authenticated'):
        try:
            user = User \
                .select() \
                .where(
                    User.is_active == True,  # noqa: E712
                    User.id == session.get('user_pk')
                ) \
                .get()
            g.user = user
            return user

        except User.DoesNotExist:
            pass


def log_in_user(username, password):
    "Logs in user using session."
    # NOTE: don't allow agents to login via UI.
    try:
        user = User.get(
            User.username == username,  # noqa: E712
            User.is_active == True,     # noqa: E712
            User.is_agent == False)     # noqa: E712

    except User.DoesNotExist:
        abort(401)

    if not user.check_password(password):
        abort(401)

    session['authenticated'] = True
    session['user_pk'] = user._pk
    g.user = user
    return user


def log_out_user():
    session.clear()
    g.user = None


def session_auth():
    "Session auth."
    return get_logged_in_user() is not None


def basic_auth():
    "Basic auth for agents."
    # NOTE: don't allow admins to login via Basic.
    auth = request.headers.get('Authorization')
    if not auth:
        return False

    username, password = b64decode(auth).split(':')

    try:
        user = User.get(
            User.username == username,  # noqa: E712
            User.is_agent == True,      # noqa: E712
            User.is_admin == False,     # noqa: E712
            User.is_active == True)     # noqa: E712

    except User.DoesNotExist:
        return False

    if not user.check_password(password):
        return False

    g.user = user
    return True


def check_auth(auth_methods=None):
    auth_methods = auth_methods or [session_auth, basic_auth]
    for auth_method in auth_methods:
        try:
            if auth_method():
                return True
        except Exception:
            LOGGER.debug('Auth error', exc_info=True)

    return False


def requires_auth(auth_methods=None):
    """
    Decorator that requires one of our auth methods for a function based view.
    """
    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if check_auth(auth_methods):
                return f(*args, **kwargs)
            abort(401)

        return inner
    return wrapper

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
            user_pk = int(session['user_pk'])

        except KeyError:
            LOGGER.info('Session user_pk missing')
            return
        except ValueError:
            LOGGER.info('Session user_pk not int %s', session['user_pk'])
            return

        try:
            user = User \
                .select() \
                .where(
                    User.is_active == True,  # noqa: E712
                    User.id == user_pk
                ) \
                .get()

            g.user = user
            return user

        except User.DoesNotExist:
            LOGGER.warning('Session user_pk %i invalid', user_pk)
            pass


def _log_in_user(username, password):
    try:
        user = User.get(
            User.username == username,  # noqa: E712
            User.is_active == True)     # noqa: E712

    except User.DoesNotExist:
        LOGGER.warning('Login failed, user not found %s', username)
        abort(401)

    if not user.check_password(password):
        LOGGER.warning('Login failed, invalid password for %s', username)
        abort(401)

    return user


def log_in_user(username, password):
    "Logs in user using session."
    user = _log_in_user(username, password)
    if user.is_agent:
        # NOTE: Agents cannot log into UI.
        LOGGER.warning('Attempted agent session login %s', username)
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
    LOGGER.debug('Performing session auth')
    return get_logged_in_user() is not None


def basic_auth():
    "Basic auth for agents."
    # NOTE: don't allow admins to login via Basic.
    LOGGER.debug('Performing basic auth')
    auth = request.headers.get('Authorization')
    if not auth:
        return False

    try:
        username, password = b64decode(auth).split(':')
    except ValueError:
        LOGGER.warning('Malformed auth header %s', auth)
        return False

    user = _log_in_user(username, password)
    if user.is_admin:
        # NOTE: admins cannot use basic auth.
        LOGGER.warning('Attempted admin basic login %s', username)
        return False

    g.user = user
    return True


def check_auth(auth_methods=None):
    auth_methods = auth_methods or [session_auth, basic_auth]
    for auth_method in auth_methods:
        try:
            if auth_method():
                LOGGER.debug('User authenticated via %s', auth_method.__name__)
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

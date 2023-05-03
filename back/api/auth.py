from functools import wraps

from flask import g, session, abort, request

from api.models import User, Agent


def get_logged_in_user():
    if session.get('authenticated'):
        if getattr(g, 'user', None):
            return g.user

        try:
            user = User \
                .select() \
                .where(
                    User.active == True,  # noqa: E712
                    User.id == session.get('user_pk')
                ) \
                .get()
            return user

        except User.DoesNotExist:
            pass


def log_in_user(username, password):
    try:
        user = User.get(
            User.username == username, User.active == True)  # noqa: E712

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
    "Check for user in session."
    return get_logged_in_user() is not None


def agent_auth():
    auth = request.headers.get('Authorization')
    if auth is None or not auth.startswith('Bearer '):
        return False
    token = auth[7:]
    try:
        agent = Agent.get(
            Agent.token == token, Agent.activated == True)  # noqa: E712

    except Agent.DoesNotExist:
        return False

    g.user = agent.user
    return True


def requires_auth(auth_methods=[session_auth]):
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

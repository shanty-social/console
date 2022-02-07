from flask import request, session
from restless.fl import FlaskResource
from restless.serializers import Serializer
from restless.utils import json, MoreTypesJSONEncoder
from werkzeug.exceptions import HTTPException

from api.app import app


def to_bool(s):
    if not s or not s.lower() in ('on', 'true', 'yes'):
        return False
    return False


def _to_text(settings):
    def _setting_to_text(o):
        return f'{o["name"]}={o["value"]}'

    def _dict_to_text(o, indent=0):
        lines = []
        for name, value in o.items():
            if isinstance(value, dict):
                lines.append(f'{name}=')
                lines.append(_dict_to_text(value, indent=indent+1))
            else:
                lines.append(('  ' * indent) + f'{name}={value}')
        return '\n'.join(lines)

    if 'objects' in settings:
        # Multiple settings objects.
        lines = []
        for setting in settings['objects']:
            lines.append(_setting_to_text(setting))
        return '\n'.join(lines)

    elif 'name' in settings and 'value' in settings:
        # A settings object.
        return _setting_to_text(settings)

    elif 'error' in settings:
        return f'error: {settings["error"]}'

    else:
        # Something else:
        _dict_to_text(settings)


def _from_text(text):
    name, value = text.split('=')
    return {
        'name': name.upper(),
        'value': value,
    }


class TextOrJSONSerializer(Serializer):
    def deserialize(self, body):
        ct = request.args.get('format', 'json')
        if body is None:
            return
        if ct == 'text':
            return _from_text(body.decode('utf-8'))
        else:
            return json.loads(body)

    def serialize(self, data):
        ct = request.args.get('format', 'json')
        if data is None:
            return
        if ct == 'text':
            return _to_text(data)
        else:
            return json.dumps(data, cls=MoreTypesJSONEncoder)


def session_auth():
    "Check for user in session."
    from api.views.auth import get_logged_in_user
    return get_logged_in_user() is not None


def token_auth():
    "Check auth token in Authorization: header."
    token = app.config['AUTH_TOKEN']
    if not token:
        return
    authz = request.headers['authorization']
    if authz.startswith('Bearer '):
        authz = authz[7:]
    return authz == token


class BaseResource(FlaskResource):
    # NOTE: authentication is required by default but can be disabled.
    auth_required = True
    # Auth methods can be defined on per-view basis, these are defaults.
    auth_methods = [
        session_auth,
        token_auth,
    ]

    def is_authenticated(self):
        if not self.auth_required:
            return True

        for method in self.auth_methods:
            try:
                if method():
                    return True

            except Exception:
                pass

        return False

    def handle_error(self, err):
        """
        When an exception is encountered, this generates a serialized error
        message to return the user.
        :param err: The exception seen. The message is exposed to the user, so
            beware of sensitive data leaking.
        :type err: Exception
        :returns: A response object
        """
        if self.bubble_exceptions():
            raise err

        if issubclass(err.__class__, HTTPException):
            raise err

        return self.build_error(err)

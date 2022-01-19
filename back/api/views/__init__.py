from flask import request
from restless.fl import FlaskResource
from restless.serializers import Serializer
from restless.utils import json, MoreTypesJSONEncoder
from werkzeug.exceptions import HTTPException


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
        if ct == 'text':
            return _from_text(body.decode('utf-8'))
        else:
            return json.loads(body)

    def serialize(self, data):
        ct = request.args.get('format', 'json')
        if ct == 'text':
            return _to_text(data)
        else:
            return json.dumps(data, cls=MoreTypesJSONEncoder)


class BaseResource(FlaskResource):
    def is_authenticated(self):
        return True

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

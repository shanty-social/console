from urllib.parse import urlparse, urlunparse
from itertools import chain

from flask import (
    make_response, jsonify, request, redirect, abort as _abort,
    url_for as _url_for,
)
from restless.fl import FlaskResource
from restless.serializers import Serializer, JSONSerializer
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RoutingException

from wtforms import Form as _Form

from api.auth import session_auth
from api.config import EXTERNAL_HOST


def url_for(*args, **kwargs):
    url = urlparse(_url_for(*args, **kwargs))
    return urlunparse(url._replace(
        scheme=EXTERNAL_HOST.scheme,
        netloc=f'{EXTERNAL_HOST.hostname}:{EXTERNAL_HOST.port}'))


def url_redir(path):
    return urlunparse(EXTERNAL_HOST._replace(path=path))


def abort(code, obj=None):
    if obj:
        _abort(make_response(jsonify(obj), code))
    else:
        _abort(code)


class RedirectResponse(HTTPException, RoutingException):
    """Raise if the map requests a redirect. This is for example the case if
    `strict_slashes` are activated and an url that requires a trailing slash.
    The attribute `new_url` contains the absolute destination url.
    The attribute `code` is returned status code.
    """
    def __init__(self, new_url, code=302):
        RoutingException.__init__(self, new_url)
        self.new_url = new_url
        self.code = code

    def get_response(self, environ):
        return redirect(self.new_url, self.code)


class MultiDict(dict):
    "MultiDict to satisfy Form."

    def getlist(self, key):
        "Get list of values for given key."
        val = self[key]
        if not isinstance(val, list):
            val = [val]
        return val

    def getall(self, key):
        "Get value as a list."
        return [self[key]]


class Form(_Form):
    "Form class allowing dictionary as data."

    def __init__(self, data, *args, **kwargs):
        data = {
            k: v for k, v in data.items() if v is not None
        }
        super().__init__(MultiDict(data), *args, **kwargs)


def try_int(v):
    try:
        return int(v)
    except ValueError:
        return v


class TextSerializer(Serializer):
    def serialize(self, body):
        def _make_paths(_parts, _obj):
            if isinstance(_obj, dict):
                items = _obj.items()
            elif isinstance(_obj, list):
                items = enumerate(_obj)
            else:
                key = '.'.join(map(str, _parts))
                value = _obj if isinstance(_obj, int) else f'"{_obj}"'
                return [f'{key}={value}']

            lines = []
            for key, value in items:
                for line in _make_paths(_parts + [key], value):
                    lines.append(line)
            return lines

        body = body.get('objects', body)
        return '\n'.join(_make_paths([], body))

    def deserialize(self, body):
        obj = dict()

        for line in [s for s in [s.strip() for s in body.split('\n')] if s]:
            path, value = line.split('=')
            parts = [try_int(v) for v in path.split('.')]
            value = value[1:-1] \
                if value.startswith('"') and value.endswith('"') \
                else try_int(value)

            _obj = obj
            for part in parts[:-1]:
                _obj = _obj.setdefault(part, dict())
            _obj[parts[-1]] = value

        def _makelists(_obj):
            for key, value in _obj.items():
                _obj[key] = _makelists(value) if isinstance(value, dict) \
                    else value
            if all([isinstance(k, int) for k in _obj.keys()]):
                return [_obj[k] for k in sorted(_obj.keys())]
            return _obj

        return _makelists(obj)


class MultiSerializer(Serializer):
    "Allow format to be requested in querystring."
    def __init__(self, **kwargs):
        self.serializers = kwargs

    @property
    def serializer(self):
        ct = request.args.get('format', 'json').lower()
        serializer = self.serializers.get(ct)
        if serializer is None:
            serializer = JSONSerializer() if not self.serializers \
                else list(self.serializers.values())[0]
        return serializer

    def serialize(self, body):
        return self.serializer.serialize(body)

    def deserialize(self, body):
        return self.serializer.deserialize(body.decode())


class BaseResource(FlaskResource):
    # NOTE: authentication is required by default but can be disabled.
    auth_required = True
    # Auth methods can be defined on per-view basis, these are defaults.
    auth_methods = [
        session_auth,
    ]
    extra_actions = {}
    extra_details = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, methods in chain(self.extra_actions.items(),
                                   self.extra_details.items()):
            self.http_methods[name] = {
                method: name for method in methods
            }

    @classmethod
    def add_url_rules(cls, app, rule_prefix, endpoint_prefix=None):
        super().add_url_rules(
            app, rule_prefix, endpoint_prefix=endpoint_prefix)
        for name, methods in cls.extra_actions.items():
            app.add_url_rule(
                rule_prefix + f'{name}/',
                endpoint=cls.build_endpoint_name(name, endpoint_prefix),
                view_func=cls.as_view(name),
                methods=methods)
        for name, methods in cls.extra_details.items():
            app.add_url_rule(
                rule_prefix + f'<pk>/{name}/',
                endpoint=cls.build_endpoint_name(name, endpoint_prefix),
                view_func=cls.as_view(name),
                methods=methods)

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

    @classmethod
    def as_view(cls, name, *init_args, **init_kwargs):
        def _wrapper(*args, **kwargs):
            inst = cls(*init_args, **init_kwargs)
            inst.request = request
            return inst.handle(name, *args, **kwargs)

        return _wrapper

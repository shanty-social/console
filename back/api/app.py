import logging
from pprint import pformat

from authlib.integrations.flask_client import OAuth

from flask import Flask, json, session
from flask_socketio import SocketIO, disconnect
from flask_peewee.db import Database
from flask_caching import Cache
from flask_session import Session

from api import config


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())


def fetch_token(name):
    LOGGER.info('Fetching token %s', name)
    return session.get(f'token.{name}')


def update_token(name, token):
    LOGGER.info('Updating token %s: %s', name, token)
    session[f'token.{name}'] = token


def delete_token(name):
    LOGGER.info('Deleting token %s', name)
    session.pop(f'token.{name}', None)


LOGGER.debug('Running with config: %s', pformat(config))

app = Flask(
    __name__, static_url_path='/static/', static_folder='../static')
app.config.from_object('api.config')

socketio = SocketIO(app, cors_allowed_origins='*', json=json)


@socketio.on('connect')
def socketio_auth():
    "Perform session authentication."
    from api.auth import get_logged_in_user
    if not get_logged_in_user():
        LOGGER.info('Websocket failed auth')
        disconnect()
    LOGGER.debug('Websocket connected')


@socketio.on('disconnect')
def socketio_disconnect():
    LOGGER.debug('Websocket disconnected')


db = Database(app)
cache = Cache(app)
oauth = OAuth(
    app, cache=cache, fetch_token=fetch_token, update_token=update_token)
for provider in config.OAUTH_PROVIDERS:
    oauth.register(
        name=provider, client_kwargs={'scope': 'openid email profile'})
Session(app)

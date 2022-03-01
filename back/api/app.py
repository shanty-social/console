import logging
from pprint import pformat

from authlib.integrations.flask_client import OAuth

from flask import Flask, json
from flask_socketio import SocketIO
from flask_peewee.db import Database
from flask_caching import Cache
from flask_session import Session

from api import config


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())


def fetch_token(name):
    from api.models import Setting
    LOGGER.info('Fetching token %s', name)
    setting = Setting.get_or_none(name=f'OAUTH_TOKEN_{name}')
    try:
        return setting.value
    except AttributeError:
        return None


def update_token(name, token):
    from api.models import Setting
    LOGGER.info('Updating token %s: %s', name, token)
    setting, created = Setting.get_or_create(
        name=f'OAUTH_TOKEN_{name}', defaults={'value': token})
    if not created:
        setting.value = token
        setting.save()


def delete_token(name):
    from api.models import Setting
    q = Setting.delete().where(Setting.name == f'OAUTH_TOKEN_{name}')
    q.execute()


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
oauth.register(name='shanty')
Session(app)

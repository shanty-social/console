import os
import logging

from authlib.integrations.flask_client import OAuth

from flask import Flask
from flask_socketio import SocketIO
from flask_peewee.db import Database
from flask_caching import Cache
from flask_session import Session


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())


def _fetch_token(name):
    from models import Setting
    return Setting.get_or_none(name=f'OAUTH_TOKEN_{name}')


def _update_token(name, token):
    from models import Setting
    setting = Setting.get_or_create(name=f'OAUTH_TOKEN_{name}')
    setting.value = token
    setting.save()


app = Flask(
    __name__, static_url_path='/static/', static_folder='../static')
app.config.from_object('api.config')

socketio = SocketIO(app)
db = Database(app)
cache = Cache(app)
oauth = OAuth(
    app, cache=cache, fetch_token=_fetch_token, update_token=_update_token)
oauth.register(name='shanty')
Session(app)

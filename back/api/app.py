import os
import logging

from flask import Flask
from flask_socketio import SocketIO
from flask_peewee.db import Database

from api.views import root


LOG_LEVEL = logging.getLevelName(
    os.environ.get('FLASK_LOG_LEVEL', 'ERROR').upper())
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(LOG_LEVEL)


app = Flask(
    __name__, static_url_path='/static/', static_folder='../static')
app.config.from_object('api.config')

socketio = SocketIO(app)
db = Database(app)

# Set up urls and views.
app.add_url_rule('/', view_func=root)


def create_tables():
    from api.models import (
        Setting, Task, TaskLog,
    )
    db.database.create_tables([Setting, Task, TaskLog], safe=True)

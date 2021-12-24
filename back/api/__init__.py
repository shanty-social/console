import os
import logging

from flask import Flask
from flask_socketio import SocketIO

from .models import db
from .views import root


LOG_LEVEL = logging.getLevelName(
    os.environ.get('FLASK_LOG_LEVEL', 'ERROR').upper())
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(LOG_LEVEL)

DB_PATH = os.environ.get('FLASK_DB_PATH', '/var/lib/db.sqlite3')

LOGGER.debug('using db: %s', DB_PATH)
app = Flask(__name__, static_url_path='/static/', static_folder='../static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://%s' % DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
socketio = SocketIO(app)

# Set up urls and views.
app.add_url_rule('/', view_func=root)

db.init_app(app)

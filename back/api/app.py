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
# Home page (in production mode, vue application.)
app.add_url_rule('/', view_func=root)


# These need models, which require db defined above.
from api.views.wifi import NetworkResource, scan  # noqa: E402
from api.views.settings import SettingResource  # noqa: E402
from api.views.services import ServiceResource  # noqa: E402

# API endpoints.
app.add_url_rule('/api/wifi/scan/', view_func=scan, methods=['POST'])
NetworkResource.add_url_rules(app, rule_prefix='/api/wifi/networks/')
SettingResource.add_url_rules(app, rule_prefix='/api/settings/')
ServiceResource.add_url_rules(app, rule_prefix='/api/services/')


def create_tables():
    "Create database tables."
    from api.models import (
        Setting, Task, TaskLog,
    )
    db.database.create_tables([Setting, Task, TaskLog], safe=True)


def drop_tables():
    "Drop database tables (used between tests)."
    from api.models import (
        Setting, Task, TaskLog,
    )
    db.database.drop_tables([Setting, Task, TaskLog], safe=True)

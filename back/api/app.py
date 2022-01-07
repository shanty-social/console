import os
import logging

from flask import Flask
from flask_socketio import SocketIO
from flask_peewee.db import Database
from flask_caching import Cache

from api.views import root


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())


app = Flask(
    __name__, static_url_path='/static/', static_folder='../static')
app.config.from_object('api.config')

socketio = SocketIO(app)
db = Database(app)
cache = Cache(app)

# Set up urls and views.
# Home page (in production mode, vue application.)
app.add_url_rule('/', view_func=root)


# These need models, which require db defined above.
from api.views.wifi import NetworkResource, scan  # noqa: E402
from api.views.settings import SettingResource  # noqa: E402
from api.views.services import ServiceResource, refresh  # noqa: E402
from api.views.tasks import TaskResource, TaskLogResource  # noqa: E402

# API endpoints.
app.add_url_rule('/api/wifi/scan/', view_func=scan, methods=['POST'])
NetworkResource.add_url_rules(app, rule_prefix='/api/wifi/networks/')
SettingResource.add_url_rules(app, rule_prefix='/api/settings/')
ServiceResource.add_url_rules(app, rule_prefix='/api/services/registry/')
app.add_url_rule(
    '/api/services/refresh/', view_func=refresh, methods=['POST'])
TaskResource.add_url_rules(app, rule_prefix='/api/tasks/')
app.add_url_rule('/api/tasks/<pk>/log/', view_func=TaskLogResource.as_list())


def create_tables():
    "Create database tables."
    import api.models
    models = [
        m for m in api.models.__dict__.values() \
            if isinstance(m, type) and issubclass(m, db.Model)
    ]
    db.database.create_tables(models, safe=True)


def drop_tables():
    "Drop database tables (used between tests)."
    import api.models
    models = [
        m for m in api.models.__dict__.values() \
            if isinstance(m, type) and issubclass(m, db.Model)
    ]
    db.database.drop_tables(models, safe=True)

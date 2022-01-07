import os
import logging


DATABASE = {
    'engine': 'peewee.SqliteDatabase',
    'name': os.environ.get('FLASK_DB_PATH', '/var/lib/db.sqlite3'),
}

DEBUG = os.environ.get('FLASK_DEBUG', '').lower() == 'true'

SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'Super secret!')

WPA_SOCKET_PATH = os.environ.get('FLASK_WPA_SOCKET_PATH', None)
NDS_SOCKET_PATH = os.environ.get('FLASK_NDS_SOCKET_PATH', None)
DOCKER_SOCKET_PATH = os.environ.get('FLASK_DOCKER_SOCKET_PATH', None)

SERVICE_URL = os.environ.get('FLASK_SERVICE_URL', None)

LOG_LEVEL = os.environ.get('FLASK_LOG_LEVEL', None)
if LOG_LEVEL:
    logging.getLogger().setLevel(
        getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    logging.getLogger().addHandler(logging.StreamHandler())

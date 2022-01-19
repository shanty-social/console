import os
import logging


def get_from_env_or_file(var_name, default=None):
    file_var_name = '%s_FILE' % var_name
    path = os.environ.get(file_var_name)
    if path and os.path.isfile(path):
        with open(path, 'r') as f:
            return f.read()
    else:
        return os.environ.get(var_name, default)
    

DATABASE = {
    'engine': 'peewee.SqliteDatabase',
    'name': os.environ.get('FLASK_DB_PATH', '/var/lib/db.sqlite3'),
}

CACHE_TYPE = os.environ.get('FLASK_CACHE_TYPE', 'SimpleCache')
CACHE_UWSGI_NAME = 'default'

DEBUG = os.environ.get('FLASK_DEBUG', '').lower() == 'true'

SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', '!Super secret!')

WPA_SOCKET_PATH = os.environ.get('FLASK_WPA_SOCKET_PATH', None)
NDS_SOCKET_PATH = os.environ.get('FLASK_NDS_SOCKET_PATH', None)
DOCKER_SOCKET_PATH = os.environ.get('FLASK_DOCKER_SOCKET_PATH', None)

SERVICE_URL = os.environ.get('FLASK_SERVICE_URL', None)

LOG_LEVEL = os.environ.get('FLASK_LOG_LEVEL', 'ERROR')

SHANTY_CLIENT_ID = os.environ.get(
    'FLASK_SHANTY_CLIENT_ID', '19bbc55f-0f6f-4fca-95bc-f86286db43da')
SHANTY_CLIENT_SECRET = get_from_env_or_file(
    'FLASK_SHANTY_CLIENT_SECRET', '50ec237f-20b0-4a47-8a25-b329f6d53beb')
SHANTY_ACCESS_TOKEN_URL = os.environ.get(
    'FLASK_SHANTY_REQUEST_TOKEN_URL', 'http://localhost:8000/api/oauth2/token/')
SHANTY_AUTHORIZE_URL = os.environ.get(
    'FLASK_SHANTY_AUTHORIZE_URL', 'http://localhost:8000/#/authorize')
SHANTY_API_BASE_URL = os.environ.get(
    'FLASK_SHANTY_API_BASE_URL', 'http://localhost:8000/api/')

SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = '/tmp'

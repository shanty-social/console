import os
import sys
from urllib.parse import urlparse, urljoin
from uuid import uuid4


def get_from_env_or_file(var_name, default=None):
    file_var_name = f'{var_name}_FILE'
    path = os.getenv(file_var_name)
    if path and os.path.isfile(path):
        with open(path, 'r') as f:
            return f.read()
    else:
        return os.getenv(var_name, default)


def get_uuid(var_name):
    try:
        path = os.environ[var_name]
    except KeyError:
        return str(uuid4())
    try:
        with open(path, 'r') as f:
            return f.read().strip()

    except FileNotFoundError:
        value = str(uuid4())
        with open(path, 'w') as f:
            f.write(value)
        return value


TEST = 'pytest' in sys.argv

DATABASE = {
    'engine': 'peewee.SqliteDatabase',
    'name': os.getenv('FLASK_DB_PATH', '/var/lib/db.sqlite3'),
}

CACHE_TYPE = os.getenv('FLASK_CACHE_TYPE', 'SimpleCache') \
    if not TEST else 'SimpleCache'
CACHE_UWSGI_NAME = 'default'

DEBUG = os.getenv('FLASK_DEBUG', '').lower() == 'true'

SECRET_KEY = os.getenv('FLASK_SECRET_KEY', '!Super secret!')

WPA_SOCKET_PATH = os.getenv('FLASK_WPA_SOCKET_PATH', None)
NDS_SOCKET_PATH = os.getenv('FLASK_NDS_SOCKET_PATH', None)
DOCKER_SOCKET_PATH = os.getenv('FLASK_DOCKER_SOCKET_PATH', None)

SERVICE_URL = os.getenv('FLASK_SERVICE_URL', None)

LOG_LEVEL = os.getenv('FLASK_LOG_LEVEL', 'ERROR')

SHANTY_BASE_URL = os.getenv(
    'FLASK_SHANTY_BASE_URL', 'http://localhost:8000/')

OAUTH_PROVIDERS = [
    {
        'name': 'shanty',
        'description': 'Default provider',
        'url': SHANTY_BASE_URL,
    },
]

SHANTY_CLIENT_ID = os.getenv(
    'FLASK_SHANTY_CLIENT_ID', '19bbc55f-0f6f-4fca-95bc-f86286db43da')

SHANTY_CLIENT_SECRET = get_from_env_or_file(
    'FLASK_SHANTY_CLIENT_SECRET', '50ec237f-20b0-4a47-8a25-b329f6d53beb')

SHANTY_API_BASE_URL = urljoin(
    SHANTY_BASE_URL,
    os.getenv('FLASK_SHANTY_API_PATH', '/api')
)

SHANTY_ACCESS_TOKEN_URL = urljoin(
    SHANTY_BASE_URL,
    os.getenv('FLASK_SHANTY_REQUEST_TOKEN_PATH', '/api/oauth2/token/')
)

SHANTY_AUTHORIZE_URL = urljoin(
    SHANTY_BASE_URL,
    os.getenv('FLASK_SHANTY_AUTHORIZE_PATH', '/#/authorize')
)

SHANTY_SERVER_METADATA_URL = urljoin(
    SHANTY_BASE_URL,
    os.getenv('FLASK_SHANTY_METADATA_PATH', '/api/oauth2/metadata/')
)

SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = os.getenv('FLASK_SESSION_FILE_DIR', '/tmp/sessions')

CERT_DIR = os.getenv('CERT_DIR', '/var/lib/certs/')

EXTERNAL_HOST = urlparse(os.getenv('EXTERNAL_HOST', 'http://localhost:8080'))

SSH_HOST = os.getenv('SSH_HOST', 'ssh.homeland-social.com')
SSH_PORT = int(os.getenv('SSH_PORT', 2222))
SSH_KEY_FILE = os.getenv('SSH_KEY_FILE', '/var/lib/console/client.key')
SSH_HOST_KEYS_FILE = os.getenv(
    'SSH_HOST_KEYS_FILE', '/var/lib/console/authorized_keys')

CONSOLE_UUID = get_uuid('FLASK_UUID_PATH')

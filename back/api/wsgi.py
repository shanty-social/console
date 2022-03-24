import sys
import logging

from uwsgi_chunked import Chunked

from api import urls  # noqa: F401
from api.app import app as _app  # noqa: F401
from api.models import create_tables, Setting
from api.tasks import start_background_tasks
from api.config import LOG_LEVEL, SSH_HOST, SSH_PORT, SSH_KEY_FILE

from conduit_client.server import SSHManagerClient


logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, LOG_LEVEL, logging.ERROR),
    force=True,
)

create_tables()
start_background_tasks()
ssh = SSHManagerClient(
    host=SSH_HOST,
    port=SSH_PORT,
    user=Setting.get_setting('CONSOLE_UUID'),
    key=SSH_KEY_FILE,
)

app = Chunked(_app)

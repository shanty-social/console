import sys
import logging

from uwsgi_chunked import Chunked

from api import urls  # noqa: F401
from api.app import app as _app  # noqa: F401
from api.models import create_tables
from api.tasks import start_background_tasks
from api.config import LOG_LEVEL


logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, LOG_LEVEL, logging.ERROR),
    force=True,
)

create_tables()
start_background_tasks()

app = Chunked(_app)

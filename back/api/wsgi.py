import sys
import logging

from api import urls     # noqa: F401
from api.app import app  # noqa: F401
from api.models import create_tables
from api.tasks import start_background_tasks

from gevent import monkey

from api.config import LOG_LEVEL


monkey.patch_thread()

logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, LOG_LEVEL, logging.ERROR),
    force=True,
)

create_tables()
start_background_tasks()

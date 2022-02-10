import sys
import logging

from api import urls  # noqa: F401
from api.app import app  # noqa: F401
from api.models import create_tables
from api.tasks import start_scheduler
from api.config import LOG_LEVEL


logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, LOG_LEVEL, logging.ERROR),
    force=True,
)

create_tables()
start_scheduler()

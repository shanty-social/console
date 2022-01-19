import os
import sys
import logging

from api.app import socketio, db, app
from api.models import create_tables
from api import urls
from api.tasks import start_scheduler
from api.config import LOG_LEVEL


logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, LOG_LEVEL, logging.ERROR),
    force=True,
)

create_tables()
start_scheduler()

import os

from api.app import socketio, db, app
from api.models import (
    Setting, Task, TaskLog,
)


HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
PORT = int(os.environ.get('FLASK_PORT', 5000))
DEBUG = os.environ.get('FLASK_DEBUG', '').lower() == 'true'


db.database.create_tables([Setting, Task, TaskLog], safe=True)
socketio.run(app, host=HOST, port=PORT, debug=DEBUG)

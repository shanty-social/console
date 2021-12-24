import os
from . import app, socketio


HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
PORT = int(os.environ.get('FLASK_PORT', 5000))
DEBUG = os.environ.get('FLASK_DEBUG', '').lower() == 'true'


socketio.run(app, host=HOST, port=PORT, debug=DEBUG)

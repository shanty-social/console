import os


DATABASE = {
    'engine': 'peewee.SqliteDatabase',
    'name': os.environ.get('FLASK_DATABASE', '//var/lib/db.sqlite3'),
}

DEBUG = os.environ.get('FLASK_DEBUG', '').lower() == 'true'

SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'Super secret!')

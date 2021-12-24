from flask import send_from_directory


def root():
    return send_from_directory('../templates', 'index.html')

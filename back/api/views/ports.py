import logging

from flask import request
from restless.resources import skip_prepare

from api.app import oauth
from api.views import BaseResource, abort


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class PortResource(BaseResource):
    extra_actions = {
        'check_port': ['POST'],
    }

    @skip_prepare
    def check_port(self):
        "Check if port is open (externally)."
        try:
            ports = map(int, request.args.getlist('ports'))

        except ValueError:
            abort(400, {'ports': 'must be integers'})

        r = oauth.shanty.post(
            '/api/utils/port_scan/', {'ports': ports})

        return r.json()

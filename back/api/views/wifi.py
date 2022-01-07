import logging

from http import HTTPStatus

from restless.preparers import FieldsPreparer
from flask import abort

from api.views import BaseResource
from api.external.wpa import Scanner


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def scan():
    scanner = Scanner.get()
    # Initiate a scan for wifi networks.
    scanner.background_scan()
    return '', HTTPStatus.NO_CONTENT


class NetworkResource(BaseResource):
    preparer = FieldsPreparer(fields={
        'frequency': 'frequency',
        'signal_level': 'signal_level',
        'flags': 'flags',
        'ssid': 'ssid',
    })

    def list(self):
        scanner = Scanner.get()
        return scanner.scanned

    def detail(self, pk):
        LOGGER.debug('Searching for network: %s', pk)
        scanner = Scanner.get()
        for network in scanner.scanned:
            if pk == network.ssid:
                return network
        abort(404, 'Not Found')

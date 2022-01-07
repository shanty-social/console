import logging

from http import HTTPStatus

import pywpas
from restless.preparers import FieldsPreparer
from flask import abort

from api.config import WPA_SOCKET_PATH
from api.views import BaseResource


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Scanner:
    _instance = None

    def __init__(self):
        crtl = pywpas.Control(sock_path=WPA_SOCKET_PATH)
        interfaces = crtl.interface_names()
        LOGGER.debug('Interfaces: %s', interfaces)
        if len(interfaces) == 0:
            LOGGER.error('Could not initialize pywpas, no interfaces!')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        elif len(interfaces) > 1:
            LOGGER.warning('More than one interface found, choosing first.')
        self._iface = crtl.interface(interfaces[0])

    @property
    def scanned(self):
        return self._iface.scanned

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = Scanner()
        return cls._instance

    def network_found(self, network):
        LOGGER.debug('Network found: %s', network.ssid)

    def background_scan(self):
        self._iface.background_scan(callback=self.network_found)


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

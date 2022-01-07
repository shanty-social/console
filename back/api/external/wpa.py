import logging

import pywpas
from api.config import WPA_SOCKET_PATH


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Scanner:
    _instance = None

    def __init__(self):
        crtl = pywpas.Control(sock_path=WPA_SOCKET_PATH)
        interfaces = crtl.interface_names()
        LOGGER.debug('Interfaces: %s', interfaces)
        if len(interfaces) == 0:
            e = Exception('Could not initialize pywpas, no interfaces!')
            LOGGER.exception('Error initializing pywpas', exc=e)
            raise e
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

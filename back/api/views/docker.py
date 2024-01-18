import socket

import requests

from flask import request, Response
from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool
from requests.adapters import HTTPAdapter

from api.config import DOCKER_SOCKET_PATH


class DockerConnection(HTTPConnection):
    def __init__(self):
        super().__init__('localhost')

    def connect(self):
        self.sock = scoket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(DOCKER_SOCKET_PATH)


class DockerConnectionPool(HTTPConnectionPool):
    def __init__(self):
        super().__init__('localhost')

    def _new_conn(self):
        return DockerConnection()


class DockerAdapter(HTTPAdapter):
    def get_connection(self, url, proxies=None):
        return DockerConnectionPool()


def proxy(path):
    """
    Proxy requests to docker unix socket.
    """
    with requests.Session() as s:
        # NOTE: this uses the adapter and unix domain socket connection
        # machinery above to proxy the request to docker daemon.
        s.mount('http://docker', DockerAdapter())

        r = s.request(
            method=request.method, url=f'http://docker/{path}',
            headers={k:v for k, v in request.headers if k.lower() != 'host'},
            data=request.get_data(), cookies=requests.cookies,
            allow_redirects=False,
        )

        # Filter out upstream headers, allow Flask to handle them instead.
        headers = [
            (k, v) for k, v in r.raw.headers.items()
            if k.lower() not in (
                'content-encoding', 'content-length', 'transfer-encoding',
                'connection'
            )
        ]

        return Response(r.content, r.status_code, headers)

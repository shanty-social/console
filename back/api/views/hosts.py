import socket
import logging

import docker

from restless.preparers import FieldsPreparer
from restless.resources import skip_prepare

from api.views import BaseResource, abort
from api.config import DOCKER_SOCKET_PATH


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def _container_details(container):
    "Get details of container."
    NetworkSettings = container.attrs['NetworkSettings']
    Config = container.attrs['Config']
    ports = [
        port for port in NetworkSettings['Ports'].keys()
        if port.endswith('/tcp')
    ]
    aliases = []
    for network in NetworkSettings['Networks'].values():
        if network['Aliases']:
            aliases.extend(network['Aliases'])
    return {
        'id': container.attrs['Id'],
        'service': Config['Labels'].get('com.docker.compose.service'),
        'image': Config['Image'],
        'aliases': aliases,
        'ports': ports,
    }


def _sniff(s, host):
    # Try to determine protocol.
    try:
        s.send(f'HTTP/1.1 GET /\r\nHost: {host}\r\n'.encode())
        reply = s.recv(128)

    except socket.error:
        return

    if not reply:
        return

    reply = reply.split(b'\r\n')[0].lower()
    LOGGER.debug('Received: %s', reply)

    if reply.startswith(b'http'):
        return 'http'
    elif b'smtp' in reply:
        return 'smtp'
    elif b'ssh' in reply:
        return 'ssh'


class HostResource(BaseResource):
    "Manage docker hosts."
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'service': 'service',
        'image': 'image',
        'ports': 'ports',
        'aliases': 'aliases',
    })
    extra_actions = {
        'port_scan': ['POST']
    }

    def list(self):
        "List potential docker hosts/ports."
        d = docker.DockerClient(base_url=f'unix://{DOCKER_SOCKET_PATH}')
        return [
            _container_details(c) for c in d.containers.list()
        ]

    def detail(self, pk):
        "Get container detail."
        d = docker.DockerClient(base_url=f'unix://{DOCKER_SOCKET_PATH}')
        return _container_details(d.containers.get(pk))

    @skip_prepare
    def port_scan():
        try:
            host = request.data['host']
        except KeyError as e:
            abort(400, {e.args[0]: 'is required'})

        try:
            ports = map(int, request.data.getlist('ports'))
        except ValueError:
            abort(400, {'ports': 'should be a list of integers'})

        if not ports:
            abort(400, {'ports': 'is required'})

        results = {}

        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)

            try:
                s.connect((host, port))
                LOGGER.debug('Connected to %s:%i', host, port)
                results[f'{host}:{port}'] = _sniff(s, host)

            except socket.error as e:
                continue

            finally:
                s.close()

        return results

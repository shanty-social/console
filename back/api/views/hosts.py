import logging

import docker

from restless.preparers import FieldsPreparer

from api.views import BaseResource
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


class HostResource(BaseResource):
    "Manage docker hosts."
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'service': 'service',
        'image': 'image',
        'ports': 'ports',
        'aliases': 'aliases',
    })

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

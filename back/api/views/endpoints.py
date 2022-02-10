import logging
import socket

import docker
import upnpy
from upnpy.exceptions import ActionNotFoundError

from flask import abort, jsonify
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer

from api.app import oauth
from api.auth import requires_auth
from api.views import BaseResource, TextOrJSONSerializer
from api.models import Endpoint
from api.config import DOCKER_SOCKET_PATH
from api.tasks import cron


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

SERVICE_PORTS = [80, 443]


def _get_gateway():
    "Get gateway via UPnP"
    upnp = upnpy.UPnP()
    upnp.discover()
    gateway = upnp.get_igd()

    # Find a service that allows adding port mappings.
    for service in gateway.get_services():
        try:
            if hasattr(service, 'AddPortMapping'):
                LOGGER.debug('Found service: %s', service)
                return gateway, service

        except ActionNotFoundError:
            continue


def _get_local_ip(host, port):
    "Get IP that is used when connecting to gateway."
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((host, port))
        return s.getsockname()[0]

    except Exception:
        return

    finally:
        s.close()


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


def _open_port(gateway, service, src_port, dst_port, host):
    host = _get_local_ip(gateway.host, gateway.port)
    service.AddPortMapping(
        NewRemoteHost='',
        NewExternalPort=src_port,
        NewProtocol='TCP',
        NewInternalPort=dst_port,
        NewInternalClient=host,
        NewEnabled=1,
        NewPortMappingDescription=f'Port mapping added by conduit for {host}:'
                                  f'{dst_port}',
        NewLeaseDuration=0)


@cron('*/5 * * * *')
def _check_endpoint_ports():
    try:
        gateway, service = _get_gateway()

    except Exception:
        LOGGER.exception('Error getting gateway')
        return

    for endpoint in Endpoint.select(Endpoint.type == 'direct'):
        if endpoint.http_port:
            _open_port(
                gateway, service, 80, endpoint.http_port, endpoint.host)
        if endpoint.https_port:
            _open_port(
                gateway, service, 443, endpoint.https_port, endpoint.host)


@requires_auth()
def open_port(host, http_port=80, https_port=443):
    "Open port in router using uPNP."
    try:
        gateway, service = _get_gateway()

    except Exception:
        LOGGER.exception('Error getting gateway')
        abort(503)

    forwards = []
    response = {
        'gateway': gateway.host,
        'forwards': forwards,
    }
    src_ports, dst_ports = SERVICE_PORTS, [http_port, https_port]
    for src_port, dst_port in zip(src_ports, dst_ports):
        destination = f'{host}:{dst_port}'
        forwards.append({'port': src_port, 'destination': destination})
        LOGGER.debug('Adding port mapping for %s', destination)
        _open_port(gateway, service, src_port, dst_port, host)
    return jsonify(response)


@requires_auth()
def check_port():
    "Check if port is open (externally)."
    r = oauth.shanty.post(
        '/api/utils/port_scan/', {'ports': SERVICE_PORTS})

    return jsonify(r.json())


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


class EndpointResource(BaseResource):
    "Manage Endpoints."
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'host': 'host',
        'port': 'port',
        'path': 'path',
        'type': 'type',
        'domain': 'domain',
    })
    serializer = TextOrJSONSerializer()

    def list(self):
        "List all endpoints."
        return Endpoint.select()

    def detail(self, pk):
        "Retrieve single endpoint."
        return get_object_or_404(Endpoint, Endpoint.name == pk)

    def create(self):
        "Create new endpoint(s)."
        try:
            name = self.data['name']
            host = self.data['host']
            port = self.data['port']
            path = self.data['path']
            type = self.data['type']
            domain = self.data['domain']
        except KeyError:
            abort(400)
        endpoint, created = Endpoint.get_or_create(
            name=name, defaults={'host': host, 'port': port, 'path': path,
                                 'type': type, 'domain': domain})
        if not created:
            endpoint.host = host
            endpoint.port = port
            endpoint.path = path
            endpoint.type = type
            endpoint.domain = domain
            endpoint.save()
        return endpoint

    def create_detail(self, pk):
        "Create single endpoint."
        try:
            host = self.data['host']
            port = self.data['port']
            path = self.data['path']
            type = self.data['type']
            domain = self.data['domain']
        except KeyError:
            abort(400)
        endpoint, created = Endpoint.get_or_create(
            name=pk, defaults={'host': host, 'port': port, 'path': path,
                               'type': type, 'domain': domain})
        if not created:
            endpoint.host = host
            endpoint.port = port
            endpoint.path = path
            endpoint.type = type
            endpoint.domain = domain
            endpoint.save()
        return endpoint

    def update(self, pk):
        "Update single endpoint."
        endpoint = get_object_or_404(Endpoint, Endpoint.name == pk)
        endpoint.host = self.data.get('host')
        endpoint.port = self.data.get('port')
        endpoint.path = self.data.get('path')
        endpoint.type = self.data.get('type')
        endpoint.domain = self.data.get('domain')
        endpoint.save()
        return endpoint

    def delete(self, pk):
        "Delete single endpoint."
        endpoint = get_object_or_404(Endpoint, Endpoint.name == pk)
        endpoint.delete_instance()

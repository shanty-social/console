import ssl
import logging

import docker

from gevent import socket

from flask import request

from restless.preparers import FieldsPreparer
from restless.resources import skip_prepare

from api.views import BaseResource, abort
from api.config import DOCKER_SOCKET_PATH


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

CONTEXT = ssl.create_default_context()
CONTEXT.check_hostname = False
CONTEXT.verify_mode = ssl.CERT_NONE


def fix_port(port):
    return int(port.split('/')[0])


def _container_details(container):
    "Get details of container."
    NetworkSettings = container.attrs['NetworkSettings']
    Config = container.attrs['Config']
    aliases, addresses, ports = set(), set(), set()
    for network in NetworkSettings['Networks'].values():
        if network.get('Aliases'):
            aliases.update(network['Aliases'])
        if network.get('IPAddress'):
            addresses.add(network['IPAddress'])
    for port in Config.get('ExposedPorts', {}).keys():
        port, type = port.split('/')
        if type == 'tcp':
            ports.add(int(port))
    aliases.remove(Config['Hostname'])
    return {
        'name': container.attrs['Name'],
        'created': container.attrs['Created'],
        'hostname': Config['Hostname'],
        'service': Config['Labels'].get('com.docker.compose.service'),
        'image': Config['Image'],
        'mode': Config.get('HostConfig', {}).get('NetworkMode'),
        'aliases': list(aliases),
        'addresses': list(addresses),
        'ports': list(ports),
    }


def _sniff_ssl(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)

    try:
        s.connect((host, port))
        with CONTEXT.wrap_socket(s) as ss:
            return str(ss.version()).lower()

    except ssl.SSLError as e:
        # Wrong version, older ssl version.
        if e.args[0] == 1:
            return 'ssl'

    except Exception:
        pass

    finally:
        s.close()


def _sniff(s, host, port):
    "Try to determine protocol."
    try:
        s.send(f'HTTP/1.1 GET /\r\nHost: {host}\r\n'.encode())
        reply = s.recv(128)

    except socket.error:
        return 'open'

    if not reply:
        reply = reply.split(b'\r\n')[0].lower()
        LOGGER.debug('Received: %s', reply)

        if reply.startswith(b'http'):
            return 'http'
        elif b'smtp' in reply:
            return 'smtp'
        elif b'ssh' in reply:
            return 'ssh'

    return _sniff_ssl(host, port) or 'open'


class HostResource(BaseResource):
    "Manage docker hosts."
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'created': 'created',
        'hostname': 'hostname',
        'service': 'service',
        'image': 'image',
        'ports': 'ports',
        'addresses': 'addresses',
        'mode': 'mode',
        'aliases': 'aliases',
    })
    extra_actions = {
        'port_scan': ['POST'],
    }

    def list(self):
        "List potential docker hosts/ports."
        filters = {}
        kwargs = {'all': False, 'filters': filters}
        try:
            filters['status'] = request.args['status']
        except KeyError:
            pass
        d = docker.DockerClient(base_url=f'unix://{DOCKER_SOCKET_PATH}')
        containers = d.containers.list(**kwargs)
        # from pprint import pprint; pprint(containers[0].attrs)
        return [
            _container_details(c) for c in containers
        ]

    def detail(self, pk):
        "Get container detail."
        d = docker.DockerClient(base_url=f'unix://{DOCKER_SOCKET_PATH}')
        return _container_details(d.containers.get(pk))

    @skip_prepare
    def port_scan(self):
        only_open = 'only_open' in request.args
        try:
            host = self.data['host']

        except KeyError as e:
            abort(400, {e.args[0]: 'is required'})

        try:
            ports = map(int, self.data['ports'])

        except KeyError:
            ports = range(1, 65535)

        except ValueError:
            abort(400, {'ports': 'should be a list of integers'})

        results_ports = {}
        results = {
            'host': host,
            'ports': results_ports,
        }
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)

            try:
                s.connect((host, port))
                if port == s.getsockname()[1]:
                    continue
                LOGGER.debug('Connected to %s:%i', host, port)
                results_ports[port] = _sniff(s, host, port)

            except socket.error:
                if not only_open:
                    results_ports[port] = 'closed'
                continue

            finally:
                s.close()

        return results

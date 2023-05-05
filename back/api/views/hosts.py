import ssl
import logging
import socket
from http import HTTPStatus

import docker
import requests
from requests.exceptions import Timeout, ConnectionError

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

LABEL_NAME_PORT_VARNAME = 'social.homefree.console.port.varname'
LABEL_NAME_PORT_DEFAULT = 'social.homefree.console.port.default'


def _get_label_int(d, key):
    try:
        return int(d[key])

    except KeyError:
        LOGGER.debug('Label %s not set', key)
    except ValueError:
        LOGGER.debug('Label %s invalid', key)

    return None


def _get_env_int(d, key):
    start = f'{key}='
    for var in d:
        if var.startswith(start):
            return var[len(start):]
    LOGGER.debug('Environment varible %s not set', key)
    return None


def _container_ports(container):
    ports = set()
    Config = container.attrs['Config']
    for port in Config.get('ExposedPorts', {}).keys():
        port, type = port.split('/')
        if type == 'tcp':
            ports.add(int(port))
    # Read port information from labels.
    label_port = None
    try:
        label_port = _get_env_int(
            Config['Env'],
            Config['Labels'][LABEL_NAME_PORT_VARNAME],
        )
    except KeyError:
        LOGGER.debug('Label %s not set', LABEL_NAME_PORT_VARNAME)
    if label_port is None:
        label_port = _get_label_int(
            Config['Labels'], LABEL_NAME_PORT_DEFAULT)
    if label_port is not None:
        ports.add(port)
    return list(ports), label_port


def _container_addresses(container):
    aliases, addresses = set(), set()
    Config = container.attrs['Config']
    NetworkSettings = container.attrs['NetworkSettings']
    for network in NetworkSettings['Networks'].values():
        if network.get('Aliases'):
            aliases.update(network['Aliases'])
        if network.get('IPAddress'):
            addresses.add(network['IPAddress'])
    aliases.add(Config['Hostname'])
    return list(aliases), list(addresses)


def _container_details(container):
    "Get details of container."
    aliases, addresses = _container_addresses(container)
    ports, default_port = _container_ports(container)
    Config = container.attrs['Config']
    NetworkSettings = container.attrs['NetworkSettings']

    return {
        'id': container.id,
        'name': container.attrs['Name'],
        'created': container.attrs['Created'],
        'hostname': Config['Hostname'],
        'labels': Config['Labels'],
        'image': Config['Image'],
        'network_mode': Config.get('HostConfig', {}).get('NetworkMode'),
        'networks': list(NetworkSettings['Networks'].keys()),
        'aliases': aliases,
        'addresses': addresses,
        'ports': ports,
        'default_port': default_port,
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
        'id': 'id',
        'name': 'name',
        'created': 'created',
        'hostname': 'hostname',
        'labels': 'labels',
        'image': 'image',
        'ports': 'ports',
        'default_port': 'default_port',
        'addresses': 'addresses',
        'network_mode': 'network_mode',
        'networks': 'networks',
        'aliases': 'aliases',
    })
    extra_actions = {
        'port_scan': ['POST'],
        'head': ['GET'],
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
    def head(self):
        try:
            url = request.args['url']

        except KeyError as e:
            abort(400, {e.args[0]: ['is required']})

        try:
            r = requests.head(url, timeout=4.0)

        except Timeout as e:
            abort(HTTPStatus.GATEWAY_TIMEOUT, {'error': str(e)})

        except ConnectionError as e:
            abort(HTTPStatus.BAD_GATEWAY, {'error': str(e)})

        if 'X-Frame-Options' in r.headers:
            # The mere existence of this header indicates problems for
            # previewing. We will override the http status code.
            abort(HTTPStatus.CONFLICT, {
                'http_status': r.status_code,
                'headers': dict(r.headers),
                'error': 'X-Frame-Options prevents preview',
            })

        return {
            'http_status': r.status_code,
            'headers': dict(r.headers),
        }

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

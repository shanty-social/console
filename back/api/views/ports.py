import logging
import socket

import upnpy
from upnpy.exceptions import ActionNotFoundError

from restless.resources import skip_prepare

import wtforms
from wtforms.validators import InputRequired

from api.app import oauth
from api.views import BaseResource,  Form, abort


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class OpenPortForm(Form):
    host = wtforms.StringField('Host', [InputRequired()])
    http_port_internal = wtforms.IntegerField('Http port', [InputRequired()])
    http_port_external = wtforms.IntegerField('Http port', [InputRequired()])
    https_port_internal = wtforms.IntegerField('Https port', [InputRequired()])
    https_port_external = wtforms.IntegerField('Https port', [InputRequired()])


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


class PortResource(BaseResource):
    extra_actions = {
        'open_port': ['POST'],
        'check_port': ['POST'],
    }

    @skip_prepare
    def open_port(self):
        "Open port in router using uPNP."
        form = OpenPortForm(self.data)
        if not form.validate():
            abort(400, form.errors)
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
        src_ports = [
            form.http_port_external.data, form.https_port_external.data
        ]
        dst_ports = [
            form.http_port_internal.data, form.https_port_internal.data
        ]
        for src_port, dst_port in zip(src_ports, dst_ports):
            destination = f'{form.host.data}:{dst_port}'
            forwards.append({'port': src_port, 'destination': destination})
            LOGGER.debug('Adding port mapping for %s', destination)
            _open_port(gateway, service, src_port, dst_port, form.host.data)
        return response

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

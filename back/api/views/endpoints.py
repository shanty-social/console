import logging
from pprint import pprint

import gevent

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer

from wtfpeewee.orm import model_form

from conduit_client.ssh import load_key, save_host_keys, Tunnel

from api.app import app, db, oauth, ssh
from api.tasks import cron, defer
from api.views import BaseResource, Form, abort
from api.models import Endpoint, Message
from api.config import CONSOLE_UUID, SSH_KEY_FILE, SSH_HOST_KEYS_FILE


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


EndpointForm = model_form(Endpoint, base_class=Form)


@cron('* * * * *')
def check_endpoint_ssh():
    "Checks ssh tunnel status."
    endpoints = list(Endpoint.select())

    try:
        ssh.ping()

    except Exception as e:
        LOGGER.exception('Error checking ssh health')
        Message.create(
            subject='SSH tunnel status',
            body=f'SSH tunnel is down, error: {e.args[0]}')
        return

    # Find which tunnels to add or remove.
    add, rem, tunnels = [], [], ssh.list_tunnels()
    for endpoint in endpoints:
        tunnel = Tunnel(endpoint.domain_name, endpoint.host, endpoint.port)
        found = any([
            tunnel == t for t in tunnels
        ])
        if not found:
            add.append(tunnel)
    for tunnel in tunnels:
        found = any([
            tunnel == t for t in add
        ])
        if not found:
            rem.append(tunnel)

    # Add and remove tunnels
    for tunnel in add:
        yield f'Setting up endpoint {endpoint.name}'
        ssh.add_tunnel(tunnel)
    for tunnel in rem:
        yield f'Removing endpoint {endpoint.name}'
        ssh.del_tunnel(tunnel)

    return f'Set up {len(endpoints)} endpoints'


def setup_endpoint_remote(domain_name, service_name):
    "Reserve domain and exchange ssh keys with server."
    def _request(method, *args, **kwargs):
        "Make an api call within app context."
        # NOTE: used as a shortcut by setup_endpoint_remote()
        with app.app_context():
            return method(*args, **kwargs)

    def _raise_if_not_status(status, r, message):
        if r.status_code != status:
            e = Exception(message)
            e.details = r.json()
            raise e

    key = load_key(path=SSH_KEY_FILE)
    shanty = getattr(oauth, service_name)
    # NOTE: these calls are done in parallel.
    calls = [
        gevent.spawn(_request, shanty.post, '/api/consoles/register/', data={
            'uuid': CONSOLE_UUID,
            'domain_name': domain_name,
            'key': key.get_base64(),
            'type': key.get_name(),
        }),
        gevent.spawn(_request, shanty.get, '/api/sshkeys/public/'),
    ]
    # Get and validate api call results.
    results = [a.get() for a in gevent.joinall(calls)]
    _raise_if_not_status(
        201, results[0], 'Failure registering console / domain')
    _raise_if_not_status(200, results[1], 'Failure fetching ssh host keys')

    # Store ssh host key where client will find it.
    save_host_keys(results[-1].json(), path=SSH_HOST_KEYS_FILE)


class EndpointResource(BaseResource):
    "Manage Endpoints."
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'name': 'name',
        'host': 'host',
        'port': 'port',
        'path': 'path',
        'domain_name': 'domain_name',
    })

    def list(self):
        "List all endpoints."
        type = request.args.get('type')
        domain_name = request.args.get('domain_name')
        host = request.args.get('host')
        endpoints = Endpoint.select()
        if type:
            endpoints = endpoints.where(Endpoint.type == type)
        if domain_name:
            endpoints = endpoints.where(Endpoint.type == domain_name)
        if host:
            endpoints = endpoints.where(Endpoint.host == host)
        return endpoints

    def detail(self, pk):
        "Retrieve single endpoint."
        return get_object_or_404(Endpoint, Endpoint.name == pk)

    def create(self):
        "Create new endpoint(s)."
        form = EndpointForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        try:
            setup_endpoint_remote(form.domain_name.data, 'shanty')
        except Exception as e:
            LOGGER.exception('Error setting up remote endpoint')
            details = {'error': e.args[0]}
            try:
                details['details'] = e.details
            except AttributeError:
                pass
            abort(400, details)
        endpoint, created = Endpoint.get_or_create(
            name=form.name.data, defaults={
                'host': form.host.data,
                'port': form.port.data,
                'path': form.path.data,
                'domain_name': form.domain_name.data,
            }
        )
        if not created:
            form.populate_obj(endpoint)
            endpoint.save()
        # NOTE: this task ensures ssh tunnels are set up.
        defer(check_endpoint_ssh)
        return endpoint

    def update(self, pk):
        "Update single endpoint."
        endpoint = get_object_or_404(Endpoint, Endpoint.name == pk)
        form = EndpointForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        form.populate_obj(endpoint)
        endpoint.save()
        return endpoint

    def delete(self, pk):
        "Delete single endpoint."
        endpoint = get_object_or_404(Endpoint, Endpoint.name == pk)
        endpoint.delete_instance()
        # NOTE: this task ensures ssh tunnels are removed.
        defer(check_endpoint_ssh)

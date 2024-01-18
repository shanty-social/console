import logging
import subprocess
import shlex

from datetime import datetime

from flask import request
from flask_peewee.utils import get_object_or_404
from restless.preparers import FieldsPreparer

from wtfpeewee.orm import model_form

from api.tasks import defer
from api.models import Service, Message
from api.views import BaseResource, Form, abort


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


ServiceForm = model_form(Container, base_class=Form)


service_preparer = FieldsPreparer(fields={
    'image': 'image',
    'tag': 'tag',
    'type': 'type',
    'definition': 'definition',
    'admin_port': 'admin_port',
    'service_port': 'service_port',
    'enabled': 'enabled',
    'started': 'started',
})


def activate_service(service):
    if service.type == 'compose':
        p = subprocess.run(
            [
                'docker-compose', '-f', '/dev/stdin',
                                  '-p', service.id, 'up', '-d'
            ],
            input=service.description, text=True, timeout=500,
        )
    elif service.type == 'command':
        args = shlex.split(service.description)
        p = subprocess.run(
            ['docker', 'run', '-d', '--name', service.id] + args, timeout=500,
        )

    try:
        p.check_returncode()

    except CalledProcessError as e:
        message = Message.create({
            'subject': f'Error starting service',
            'body': str(e),
        })
        raise

    service.started = datetime.now()
    service.save()


def deactivate_service(service, remove=False):
    if service.type == 'compose':
        p = subprocess.run(
            [
                'docker-compose', '-f', '/dev/stdin', '-p', service.id, 'down'
            ],
            input=service.description, text=True, timeout=500,
        )
    elif service.type == 'command':
        p = subprocess.run(
            ['docker', 'kill', service.id], timeout=500,
        )

    try:
        p.check_returncode()
    
    except CalledProcessError as e:
        message = Message.create({
            'subject': f'Error starting service',
            'body': str(e),
        })
        raise

    if remove:
        service.delete_instance()


def modify_service(service):
    deactivate_service(service)
    activate_service(service)


class ServiceResource(BaseResource):
    "Manage docker services."
    preparer = service_preparer

    def list(self):
        "List all services."
        return Service.select()

    def detail(self, pk):
        "Retrieve single service."
        return get_object_or_404(Service, Service.id == pk)

    def create(self):
        "Create new docker service."
        form = ServiceForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        service = Service.create({
            'image': form.image.data,
            'tag': form.tag.data,
            'type': form.type.data,
            'definition': form.definition.data,
            'admin_port': form.admin_port.data,
            'service_port': form.service_port.data,
            'enabled': form.enabled.data,
        })
        defer(activate_service, args=(service,))
        return service

    def delete(self, pk):
        "Delete docker service."
        service = get_object_or_404(Service, Service.id == pk)
        service.enabled = False
        service.save()
        defer(deactivate_service, args=(service,), kwargs={'remove': True})

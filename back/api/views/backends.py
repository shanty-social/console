import logging

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer

from wtfpeewee.orm import model_form

from api.views import BaseResource, Form, abort
from api.models import Backend


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


BackendForm = model_form(Backend, base_class=Form)


backend_preparer = FieldsPreparer(fields={
    'id': 'id',
    'name': 'name',
    'url': 'url',
    'container_id': 'container_id',
})


class BackendResource(BaseResource):
    "Manage Backends."
    preparer = backend_preparer

    def list(self):
        "List backends."
        name = request.args.get('name')
        url = request.args.get('url')
        host = request.args.get('host')
        backends = Backend.select()
        if name:
            backends = backends.where(Backend.name == name)
        if url:
            backends = backends.where(Backend.url == url)
        if host:
            backends = backends.where(Backend.host == host)
        return backends

    def detail(self, pk):
        "Retrieve single backend."
        return get_object_or_404(Backend, Backend.id == pk)

    def create(self):
        "Create new backend(s)."
        form = BackendForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        backend, created = Backend.get_or_create(
            name=form.name.data, defaults={
                'name': form.addr.name,
                'url': form.url.data,
                'host': form.host.data,
            }
        )
        if not created:
            form.populate_obj(backend)
            backend.save()
        return backend

    def update(self, pk):
        "Update single backend."
        backend = get_object_or_404(Backend, Backend.id == pk)
        form = BackendForm(self.data, obj=backend)
        if not form.validate():
            abort(400, form.errors)
        form.populate_obj(backend)
        backend.save()
        return backend

    def delete(self, pk):
        "Delete single backend."
        backend = get_object_or_404(Backend, Backend.id == pk)
        backend.delete_instance()

import logging


from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer

from wtfpeewee.orm import model_form

from api.views import BaseResource, Form, abort
from api.models import Frontend


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


FrontendForm = model_form(Frontend, base_class=Form)

frontend_preparer = FieldsPreparer(fields={
    'id': 'id',
    'type': 'type',
    'backend': 'backend',
    'url': 'url',
})


class FrontendResource(BaseResource):
    "Manage Backends."
    preparer = frontend_preparer

    def list(self):
        "List backends."
        type = request.args.get('type')
        backend = request.args.get('backend')
        url = request.args.get('url')
        frontends = Frontend.select()
        if type:
            frontends = frontends.where(Frontend.type == type)
        if backend:
            frontends = frontends.where(Frontend.url == backend)
        if url:
            frontends = frontends.where(Frontend.url == url)
        return frontends

    def detail(self, pk):
        "Retrieve single frontend."
        return get_object_or_404(Frontend, Frontend.id == pk)

    def create(self):
        "Create new frontend(s)."
        form = FrontendForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        frontend, created = Frontend.get_or_create(
            url=form.url.data, defaults={
                'type': form.addr.type,
                'backend': form.host_name.backend,
            }
        )
        if not created:
            form.populate_obj(frontend)
            frontend.save()
        return frontend

    def update(self, pk):
        "Update single frontend."
        frontend = get_object_or_404(Frontend, Frontend.id == pk)
        form = FrontendForm(self.data, obj=frontend)
        if not form.validate():
            abort(400, form.errors)
        form.populate_obj(frontend)
        frontend.save()
        return frontend

    def delete(self, pk):
        "Delete single frontend."
        frontend = get_object_or_404(Frontend, Frontend.id == pk)
        frontend.delete_instance()

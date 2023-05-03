import logging

# import gevent

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer
# from restless.resources import skip_prepare

from wtfpeewee.orm import model_form

# from api.app import oauth
from api.views import BaseResource, Form, abort
from api.models import Frontend  # , CryptoKey
# from api.config import CONSOLE_UUID


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


FrontendForm = model_form(Frontend, base_class=Form)


def raise_if_not_status(status, r, message):
    "Raise exception if oauth request returns unexpected status"
    if r.status_code != status:
        e = Exception(message)
        e.details = r.json()
        raise e


frontend_preparer = FieldsPreparer(fields={
    'id': 'id',
    'type': 'type',
    'backend': 'backend',
    'url': 'url',
})


class FrontendResource(BaseResource):
    "Manage Backends."
    preparer = frontend_preparer
    # extra_details = {
    #     'ssh_key': ['POST'],
    # }

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

    # @skip_prepare
    # def ssh_key(self, pk):
    #     "Associate SSH public key with domain, return host public key."
    #     try:
    #         key = self.data['key']
    #     except KeyError as e:
    #         abort(400, {e.args[0]: 'is required'})
    #     shanty = getattr(oauth, 'shanty')
    #     frontend = get_object_or_404(Frontend, Frontend.id == pk)
    #     frontend.ssh_key = CryptoKey.create(type=1, provision=1, public=key)

    #     # NOTE: these calls are done in parallel.
    #     calls = [
    #         gevent.spawn(shanty.post, '/api/consoles/register/', data={
    #             'uuid': CONSOLE_UUID,
    #             'domain_name': frontend.url.host,
    #             'key': key.get_base64(),
    #             'type': key.get_name(),
    #         }),
    #         gevent.spawn(shanty.get, '/api/sshkeys/public/'),
    #     ]

    #     # Get and validate api call results.
    #     results = [a.get() for a in gevent.joinall(calls)]
    #     raise_if_not_status(
    #         201, results[0], 'Failure registering console / domain')
    #     raise_if_not_status(
    #         200, results[1], 'Failure fetching ssh host keys')

    #     host_key = results[1].json()
    #     frontend.host_key = host_key['key']
    #     frontend.save()

    #     # Return host key to caller.
    #     return {
    #         'host_key': host_key,
    #     }

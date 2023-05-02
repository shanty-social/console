import logging

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer

from wtfpeewee.orm import model_form

from api.views import BaseResource, Form, abort
from api.models import CryptoKey


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


CryptoKeyForm = model_form(CryptoKey, base_class=Form)


cryptokey_preparer = FieldsPreparer(fields={
    'id': 'id',
    'type': 'type',
    'provision': 'provision',
    'private': 'private',
    'public': 'public',
    'created': 'created',
})


class CryptoKeyResource(BaseResource):
    "Manage CryptoKeys."
    preparer = cryptokey_preparer

    def list(self):
        "List crypto keys."
        type = request.args.get('type')
        provision = request.args.get('provision')
        private = request.args.get('private')
        public = request.args.get('public')
        cryptokeys = CryptoKey.select()
        if type:
            cryptokeys = cryptokeys.where(CryptoKey.type == type)
        if provision:
            cryptokeys = cryptokeys.where(CryptoKey.provision == provision)
        if private:
            cryptokeys = cryptokeys.where(CryptoKey.private == private)
        if public:
            cryptokeys = cryptokeys.where(CryptoKey.public == public)
        return cryptokeys

    def detail(self, pk):
        "Retrieve single crypto key."
        return get_object_or_404(CryptoKey, CryptoKey.id == pk)

    def create(self):
        "Create new crypto key(s)."
        form = CryptoKeyForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        cryptokey, created = CryptoKey.get_or_create(
            name=form.name.data, defaults={
                'type': form.type.data,
                'provision': form.provision.data,
                'private': form.private.data,
                'public': form.public.data,
            }
        )
        if not created:
            form.populate_obj(cryptokey)
            cryptokey.save()
        return cryptokey

    def update(self, pk):
        "Update single cryptokey."
        cryptokey = get_object_or_404(CryptoKey, CryptoKey.id == pk)
        form = CryptoKeyForm(self.data)
        if not form.validate():
            abort(400, form.errors)
        form.populate_obj(cryptokey)
        cryptokey.save()
        return cryptokey

    def delete(self, pk):
        "Delete single cryptokey."
        cryptokey = get_object_or_404(CryptoKey, CryptoKey.id == pk)
        cryptokey.delete_instance()

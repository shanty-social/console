import logging
from datetime import datetime, timedelta

import gevent

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer
from restless.resources import skip_prepare

from wtfpeewee.orm import model_form

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from api.views import BaseResource, Form, abort
from api.models import CryptoKey, Frontend
from api.app import oauth, db, app
from api.auth import get_logged_in_user


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


CryptoKeyForm = model_form(CryptoKey, base_class=Form, exclude=['user'])


cryptokey_preparer = FieldsPreparer(fields={
    'id': 'id',
    'type': 'type',
    'provision': 'provision',
    'user': 'user',
    'private': 'private',
    'public': 'public',
    'created': 'created',
})


def app_request(method, *args, **kwargs):
    "Make an api call within app context."
    # NOTE: used as a shortcut by setup_endpoint_remote()
    with app.app_context():
        return method(*args, **kwargs)


def raise_if_not_status(status, r, message):
    "Raise exception if oauth request returns unexpected status"
    if r.status_code != status:
        e = Exception(message)
        e.details = r.json()
        raise e


def generate_ca(hostname='console.local', type='ssl-rsa'):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])
    san = x509.SubjectAlternativeName([x509.DNSName(hostname)])
    basic_constraints = x509.BasicConstraints(ca=True, path_length=1)
    now = datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(1000)
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=10*365))
            .add_extension(basic_constraints, False)
            .add_extension(san, False)
            .sign(key, hashes.SHA256(), default_backend())
    )
    ca_cryptokey = CryptoKey.create(
        type=type,
        provision='internal',
        name='CA',
        public=cert.public_bytes(
            encoding=serialization.Encoding.PEM).decode('utf8'),
        private=key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode('utf8'),
    )
    return ca_cryptokey


def generate_certificate(hostname, type='ssl-rsa', alternative_names=None,
                         ca_cryptokey=None):
    if ca_cryptokey is None:
        try:
            ca_cryptokey = CryptoKey.get(
                CryptoKey.type == type, CryptoKey.name == 'CA')
        except CryptoKey.DoesNotExist:
            ca_cryptokey = generate_ca(type=type)

    ca_cert = x509.load_pem_x509_certificate(
        ca_cryptokey.public.encode('utf8'))
    ca_key = serialization.load_pem_private_key(
        ca_cryptokey.private.encode('utf8'), password=None)

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])
    san = x509.SubjectAlternativeName([x509.DNSName(hostname)])
    basic_constraints = x509.BasicConstraints(ca=False, path_length=None)
    now = datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(ca_cert.issuer)
            .public_key(key.public_key())
            .serial_number(1000)
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=10*365))
            .add_extension(basic_constraints, False)
            .add_extension(san, False)
            .sign(ca_key, hashes.SHA256(), default_backend())
    )
    cryptokey = CryptoKey.create(
        type=type,
        provision='internal',
        name=hostname,
        public=cert.public_bytes(
            encoding=serialization.Encoding.PEM).decode('utf8'),
        private=key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode('utf8'),
    )
    return cryptokey


class CryptoKeyResource(BaseResource):
    "Manage CryptoKeys."
    preparer = cryptokey_preparer
    extra_actions = {
        'issue': ['POST'],
        'sshkey': ['POST'],
    }

    def list(self):
        "List crypto keys."
        type = request.args.get('type')
        provision = request.args.get('provision')
        agent_id = request.args.get('agent_id')
        private = request.args.get('private')
        public = request.args.get('public')
        cryptokeys = CryptoKey.select()
        if type:
            cryptokeys = cryptokeys.where(CryptoKey.type == type)
        if provision:
            cryptokeys = cryptokeys.where(CryptoKey.provision == provision)
        if agent_id:
            cryptokeys = cryptokeys.where(CryptoKey.agent_id == agent_id)
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
                'user': get_logged_in_user(),
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
        form = CryptoKeyForm(self.data, obj=cryptokey)
        if not form.validate():
            abort(400, form.errors)
        form.populate_obj(cryptokey)
        cryptokey.save()
        return cryptokey

    def delete(self, pk):
        "Delete single cryptokey."
        cryptokey = get_object_or_404(CryptoKey, CryptoKey.id == pk)
        cryptokey.delete_instance()

    def issue(self):
        "Issue SSL CA signed key / cert."
        try:
            frontend = get_object_or_404(
                Frontend, Frontend.id == self.data['frontend_id'])
        except KeyError as e:
            abort(400, {e.args[0]: 'is required'})

        cryptokey = generate_certificate(frontend.url.hostname)
        return cryptokey

    @skip_prepare
    def sshkey(self):
        "Store SSH public key and host key."
        LOGGER.info('saving')
        form = CryptoKeyForm(
            self.data,
            provision='internal',
            name='Conduit client public ssh key',
        )
        if not form.validate():
            abort(400, form.errors)
        with db.database.atomic():
            CryptoKey.create(
                name=form.name.data,
                type=form.type.data,
                provision=form.provision.data,
                public=form.public.data,
            )
            shanty = getattr(oauth, 'shanty')
            LOGGER.info('saved')

            # NOTE: these calls are done in parallel.
            user = get_logged_in_user()
            calls = [
                gevent.spawn(
                    app_request, shanty.post, '/api/consoles/register/', data={
                        'type': form.type.data,
                        'key': form.public.data,
                        'uuid': user.username,
                    }
                ),
                gevent.spawn(app_request, shanty.get, '/api/sshkeys/public/'),
            ]

            # Get and validate api call results.
            results = [a.get() for a in gevent.joinall(calls)]
            raise_if_not_status(
                201, results[0], 'Failure registering console / domain')
            raise_if_not_status(
                200, results[1], 'Failure fetching ssh host keys')

            # Save host keys.
            for host_key in results[1].json():
                CryptoKey.create(
                    name=f'Conduit server host key {host_key["type"]}',
                    type=host_key['type'],
                    provision='internal',
                    public=host_key['key'],
                )

        return 200

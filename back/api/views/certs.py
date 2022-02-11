import certsign

from flask import send_from_directory

from api.views import BaseResource
from api.auth import token_auth
from api.tasks import cron


ACME_DIR = '/var/tmp/acme/'


@cron('0 0 1,10,20 * *')
def renew_certs():
    pass


def acme(path):
    """
    Exposes acme-challenges for obtaining certificates.
    """
    return send_from_directory(ACME_DIR, path)


class CertResource(BaseResource):
    def is_authenticated(self):
        # Allow read access with token auth.
        if super().is_authenticated():
            return True

        if self.request_method() == 'GET' and token_auth():
            return True

        return False

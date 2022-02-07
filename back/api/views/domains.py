from restless.preparers import FieldsPreparer

from api.views import BaseResource
from api.models import Domain


class DomainResource(BaseResource):
    "Domains."
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'provider': 'provider',
        'options': 'options',
    })

    def list(self, pk):
        pass

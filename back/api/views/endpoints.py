from restless.preparers import FieldsPreparer

from api.views import BaseResource
from api.models import Endpoint


class EndpointResource(BaseResource):
    "Domains."
    preparer = FieldsPreparer(fields={
        'name': 'name',
        'host': 'host',
        'port': 'port',
        'type': 'type',
        'domain': 'domain',
    })

    def list(self, pk):
        pass

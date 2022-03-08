import subprocess
from io import BytesIO

from mkpy224o import find_keys

from flask import request
from flask_peewee.utils import get_object_or_404

from restless.preparers import FieldsPreparer
from restless.resources import skip_prepare

from api.views import BaseResource
from api.views.tasks import task_preparer
from api.models import Task, TaskLog, Torkey
from api.tasks import defer


def _find_key(prefix, task):
    prefix_re = '^' + prefix if prefix else ''
    key = find_keys(prefix_re, count=1, interval=3, on_progress=task.logger)[0]
    key = Torkey.create(prefix=prefix, **key)
    return {
        'key_id': key.id,
        'hostname': key.hostname,
    }


class TorResource(BaseResource):
    "Handles tor config, including vanity addresses."
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'prefix': 'prefix',
        'hostname': 'hostname',
    })
    extra_actions = {
        'generate': ['POST'],
    }

    def list(self):
        return Torkey.select()

    def detail(self, pk):
        "Retrieve single task."
        return get_object_or_404(Torkey, Torkey.id == pk)

    def delete(self, pk):
        "Delete task."
        torkey = get_object_or_404(Torkey, Torkey.id == pk)
        torkey.delete_instance()

    @skip_prepare
    def generate(self):
        # When vanity address is not provided, search for any address.
        prefix = self.data.get('prefix', '.*')
        return task_preparer.prepare(
            defer(_find_key, args=(prefix,), task_kwarg=True))

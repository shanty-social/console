import subprocess
from io import BytesIO

from mkpy224o import find_keys

from flask import request

from restless.preparers import FieldsPreparer

from api.views import BaseResource
from api.models import Task, TaskLog, Torkey
from api.tasks import defer


def _find_key(prefix, task):
    def on_progress(stats):
        task.tail = TaskLog.create(task=task, message=stats)
        task.save()

    key = find_keys(prefix, count=1, on_progress=on_progress)[0]
    key = Torkey.create(prefix=prefix, **key)
    return {
        'key_id': key.id,
        'hostname': key.hostname,
    }


class TorResource(BaseResource):
    "Handles tor config, including vanity addresses."
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'created': 'created',
        'tail': 'tail',
    })
    extra_actions = {
        'generate': ['POST'],
    }

    def generate(self):
        # When vanity address is not provided, search for any address.
        prefix = self.data.get('prefix', '.*')
        if prefix:
            prefix = '^' + prefix
        return defer(_find_key, args=(prefix,), pass_task_as=True)

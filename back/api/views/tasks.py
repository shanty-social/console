import logging

from restless.preparers import FieldsPreparer, SubPreparer
from flask import request
from flask_peewee.utils import get_object_or_404

from api.models import Task, TaskLog
from api.views import BaseResource, TextOrJSONSerializer
from api.tasks import cron


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


exc_preparer = FieldsPreparer(fields={
    'type': 'type',
    'value': 'value',
})


class ResultPreparer(FieldsPreparer):
    "Handle special cases."

    def lookup_data(self, lookup, data):
        "function and result fields are callables that we don't want called."
        if lookup == 'function':
            return data.function.__name__
        elif lookup == 'result':
            try:
                return data.get_result()
            except Exception as e:
                return exc_preparer.prepare({
                    'type': e.__class__.__name__,
                    'value': str(e),
                })
        return super().lookup_data(lookup, data)


class TaskResource(BaseResource):
    "Manage settings."
    preparer = ResultPreparer(fields={
        'id': 'id',
        'function': 'function',
        'args': 'args',
        'kwargs': 'kwargs',
        'result': 'result',
        'created': 'created',
        'completed': 'completed',
        'tail': 'tail.message',
    })

    def list(self):
        "List all tasks."
        return Task.select()

    def detail(self, pk):
        "Retrieve single task."
        return get_object_or_404(Task, Task.id == pk)

    def delete(self, pk):
        "Delete task."
        task = get_object_or_404(Task, Task.id == pk)
        task.delete_instance()


class TaskLogResource(BaseResource):
    "Log output for a task."
    preparer = FieldsPreparer(fields={
        'created': 'created',
        'message': 'message',
    })

    def list(self, pk):
        task = get_object_or_404(Task, Task.id == pk)
        return TaskLog.select().where(TaskLog.task == task).order_by(Task.created.desc())

import threading
import inspect
import logging

from datetime import datetime

from stopit import threading_timeoutable, TimeoutException

from api.app import db, app
from api.models import Task, TaskLog


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class CancelledError(Exception):
    pass


def _wrap_generator(task):
    def wrapper(*args, **kwargs):
        LOGGER.debug(
            'Wrapping generator task function: %s', task.function)
        gen = task.function(*args, **kwargs)

        while True:
            try:
                l = TaskLog(task=task, message=next(gen))
                LOGGER.debug('Task[%i] log: %s', task.id, l.message)
                l.save()
                (Task
                    .update(tail=l)
                    .where(Task.id==task.id)).execute()

            except StopIteration as e:
                return e.value

    return wrapper


@threading_timeoutable()
def _task_runner(task):
    if inspect.isgeneratorfunction(task.function):
        runnable = _wrap_generator(task)
    else:
        runnable = task.function

    result = None
    try:
        LOGGER.debug('Task[%i] starting...', task.id)
        result = task.function(*task.args, **task.kwargs)
        LOGGER.debug('Task[%i] result: %s', task.id, result)

    except (TimeoutException, CancelledError) as e:
        result = e

    except Exception as e:
        LOGGER.exception('Task[%i] error', task.id)
        result = e

    finally:
        LOGGER.debug('Task[%i] completed...', task.id)

    # Update task information
    LOGGER.debug('Task[%i] saving...', task.id)
    (Task
        .update(
            result=result,
            completed=datetime.now(),
        )
        .where(Task.id==task.id)).execute()


def defer(f, *args, **kwargs):
    timeout = kwargs.pop('timeout', None)
    task = Task(function=f, args=args, kwargs=kwargs)
    task.save()  # Save to get an id assigned.
    t = threading.Thread(
        target=_task_runner, args=(task,), kwargs={'timeout': timeout},
        daemon=False)
    t.start()
    task.ident = t.ident
    (Task.update(ident=t.ident).where(Task.id==task.id)).execute()
    LOGGER.debug('Task[%i] started: %s', task.id, task.ident)
    return task

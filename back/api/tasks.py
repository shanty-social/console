import threading
import inspect
import logging

from datetime import datetime

import pycron
from stopit import threading_timeoutable, TimeoutException

from playhouse.signals import post_save

from api.models import Task, TaskLog


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

CRON = None
CRONTAB = []


class CancelledError(Exception):
    pass


def _wrap_generator(task):
    def wrapper(*args, **kwargs):
        LOGGER.debug(
            'Wrapping generator task function: %s', task.function)
        gen = task.function(*args, **kwargs)

        while True:
            try:
                task.logger(next(gen))

            except StopIteration as e:
                return e.value

    return wrapper


# NOTE: timeout kwarg is consumed by this decorator.
@threading_timeoutable()
def _task_runner(task, task_kwarg=None):
    if inspect.isgeneratorfunction(task.function):
        runnable = _wrap_generator(task)
    else:
        runnable = task.function

    kwargs = task.kwargs.copy()
    if task_kwarg:
        kwargs[task_kwarg] = task

    result = None
    try:
        LOGGER.debug('Task[%s] starting...', task.id)
        result = runnable(*task.args, **kwargs)
        LOGGER.debug('Task[%s] result: %s', task.id, result)

    except (TimeoutException, CancelledError) as e:
        LOGGER.info('Task[%s] timeout/cancelled', task.id)
        result = e

    except Exception as e:
        LOGGER.exception('Task[%s] error', task.id)
        result = e

    finally:
        LOGGER.debug('Task[%s] completed...', task.id)

    # Update task information
    LOGGER.debug('Task[%s] saving...', task.id)
    task.result = result
    task.completed = datetime.now()
    task.save()


def cron(schedule, *args, **kwargs):
    "Decorate a function to define a run schedule and arguments."
    def inner(f):
        LOGGER.info('Scheduling task %s at %s', f.__name__, schedule)
        CRONTAB.append((schedule, f, args, kwargs))
        return f
    return inner


class RepeatTimer(threading.Timer):
    def __init__(self, *args, **kwargs):
        daemon = kwargs.pop('daemon', None)
        super().__init__(*args, **kwargs)
        self.daemon = bool(daemon)

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if self.finished.is_set():
                break
            try:
                self.function(*self.args, **self.kwargs)

            except Exception:
                LOGGER.exception('Error in timer function.')


def start_scheduler(interval=60.0):
    "Start a scheduler to run schedule cron tasks."
    global CRON

    def _scheduler():
        LOGGER.debug('Scheduler checking %i tasks', len(CRONTAB))
        for schedule, f, args, kwargs in CRONTAB:
            if pycron.is_now(schedule):
                LOGGER.debug(
                    'Schedule %s is now, executing task %s', schedule, f)
                defer(f, args, kwargs)

    LOGGER.info('Starting task scheduler for %i tasks', len(CRONTAB))
    CRON = RepeatTimer(interval, _scheduler, daemon=True)
    CRON.start()


def stop_scheduler():
    "Terminate the scheduler."
    global CRON
    CRON.cancel()
    CRON = None


def defer(f, args=(), kwargs={}, timeout=None,
          task_kwarg=None, pass_log_kwarg=None):
    "Defer a function to run as a task."
    runner_kwargs = {
        'timeout': timeout,
        'task_kwarg': 'task' if task_kwarg is True else task_kwarg
    }
    task = Task(function=f, args=args, kwargs=kwargs)
    task.save(force_insert=True)  # Save to get an id assigned.
    t = threading.Thread(target=_task_runner, args=(task,),
        kwargs=runner_kwargs, daemon=False, name=str(task.id))
    t.start()
    LOGGER.debug('Task[%s] started', task.id)
    return task


def find_thread(uuid):
    for t in threading.enumerate():
        LOGGER.debug('Comparing %s == %s', t.name, uuid)
        if t.name == uuid:
            LOGGER.debug('Task[%s] found', uuid)
            return t

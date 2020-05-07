from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coursebio.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('coursebio')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

from celery.schedules import crontab
app.conf.beat_schedule = {
    # 'add-every-minute-contrab': {
    #     'task': 'courses.tasks.create_post',
    #     'schedule': crontab(),
    #     'args': (),
    # },
    # Executes every Monday morning at 7:30 a.m.
    'add-every-monday-morning': {
        'task': 'courses.tasks.udemy',
        'schedule': crontab(hour=7, minute=30, day_of_week=1),
        'args': (),
    },
    'add-every-5-seconds': {
        'task': 'courses.tasks.create_post',
        'schedule': 5.0,
        'args': ()
    },
    'add-every-minute-contrab': {
        'task': 'courses.tasks.udemy',
        'schedule': crontab(),
        'args': ()
    },
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
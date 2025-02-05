from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings

from celery import Celery
from celery.schedules import crontab


corn_settings = 'rentshop.settings_staging'

if os.getenv('TRP_CRON_SETTING'):
    corn_settings = os.getenv('TRP_CRON_SETTING')


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', corn_settings)

app = Celery('trp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

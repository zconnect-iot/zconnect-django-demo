from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_demo.settings')

app = Celery('django_demo')

# Using a string here means the worker doesn't have to serialize the
# configuration object to child processes.
#
# *** Do not set prefix="CELERY" ***
# setting namespace='CELERY' would mean that all celery-related configuration
# keys would have to have a `CELERY_` prefix. This conflicts with setting up
# celerybeat which has a config key with a CELERYBEAT_ prefix
app.config_from_object('django.conf:settings', namespace="CELERY")
# app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

__version__ = "0.0.1"

# FIXME
# celery docs:
# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
# suggest doing this, but it doesn't work because the apps aren't finished
# loading by the time it imports the tasks etc. (which in turn import models).
# Need to either import all models INSIDE tasks, or start the celery app a
# different way.
# from ._tasks import app as celery_app

default_app_config = 'zconnect.apps.ZconnectAppConfig'

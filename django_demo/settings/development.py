# pylint: disable=unused-wildcard-import, wildcard-import
# Python imports
import os
from os.path import abspath, dirname, join

import yaml
import uuid

# project imports
from .common import *


def load_key(filename):
    """Load a file from KEY_ROOT"""
    return read_file_into_var(join(KEY_ROOT, "development", filename))


# uncomment the following line to include i18n
# from .i18n import *


# ##### DEBUG CONFIGURATION ###############################
DEBUG = True

# allow all hosts during development
ALLOWED_HOSTS = ['*']

# adjust the minimal login
LOGIN_URL = 'core_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'core_login'

CORS_ORIGIN_ALLOW_ALL = True

SIMPLE_JWT.update({
    "ALGORITHM": "RS256",
    "SIGNING_KEY": load_key("private.pem"),
    "VERIFYING_KEY": load_key("public.pem"),
})


# ##### DATABASE CONFIGURATION ############################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(PROJECT_ROOT, 'run', 'demo.sqlite3'),
    }
}

REDIS = {
    "connection": {
        "username": None,
        "password": None,
        "host": os.getenv('REDIS_HOST', '127.0.0.1'),
        "port": 6379,
    },
    "event_definition_evaluation_time_key": 'event_def_eval',
    "event_definition_state_key": 'event_def_state',
    # If an ev def hasn't been evaluated before, ev time will be set to
    # datetime.utcnow() + this offset.
    "event_definition_evaluation_time_clock_skew_offset": 5,
    "online_status_threshold_mins": 10,
}

# ##### CELERY CONFIGURATION ##############################

# makes it behave synchronously for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ##### APPLICATION CONFIGURATION #########################

INSTALLED_APPS = DEFAULT_APPS

REST_FRAMEWORK.update({
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        # 'zconnect.permissions.GroupPermissions',
    ],
})

ZCONNECT_SETTINGS = {
    "SENDER_SETTINGS": {
        "cls": "zconnect.messages.IBMInterface",
        "type": "shared",

        "broker-url": "vernemq",
        "full_client_id": "zconnect-sender-{}".format(uuid.uuid4()),
        "id": "test_sender",
        "disable-tls": True,
        "port": 1883,
        "auth-method": "token",
        "auth-key": "overlock-worker",
        "auth-token": "123456789",
    },
    "LISTENER_SETTINGS": {
        "cls": "zconnect.messages.IBMInterface",
        "type": "shared",

        "broker-url": "vernemq",
        "full_client_id": "zconnect-listener-{}".format(uuid.uuid4()),
        "id": "test_sender",
        "disable-tls": True,
        "port": 1883,
        "auth-method": "token",
        "auth-key": "overlock-worker",
        "auth-token": "123456789",

        **DEFAULT_LISTENER_SETTINGS,
    },
}

ENABLE_STACKSAMPLER = False

here = dirname(abspath(__file__))

with open(join(here, "colorlog.yaml")) as log_cfg_file:
    LOGGING = yaml.load(log_cfg_file)

####################### Development security overrides ########################

# If set to true (as they should be on production) these cause issues with non-
# HTTPS connections.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

########################### Email Configuration ###############################
EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'
# THIS API KEY IS FOR DEVELOPMENT ONLY!
SPARKPOST_API_KEY = '609adece54b68c1d47857914bfbeada737c24676'


# ##### SECURITY CONFIGURATION ############################

# Fix /admin login issue with non-HTTPS local deployments
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# We store the secret key here
# The required SECRET_KEY is fetched at the end of this file
SECRET_FILE = normpath(join(PROJECT_ROOT, 'run', 'SECRET.key'))

# finally grab the SECRET KEY
try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    from django.utils.crypto import get_random_string
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!$%&()=+-_'
    SECRET_KEY = get_random_string(50, chars)
    try:
        with open(SECRET_FILE, 'w') as f:
            f.write(SECRET_KEY)
    except IOError:
        raise Exception('Could not open %s for writing!' % SECRET_FILE)

################################ EMAIL CONFIG ##################################

DEFAULT_FROM_EMAIL = "admin@zoetrope.io"

FRONTEND_PROTOCOL = 'https'
FRONTEND_DOMAIN = 'localhost:3000'

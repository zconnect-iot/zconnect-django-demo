"""Integration settings

REQUIRED environment variables

    REDIS_USERNAME
    REDIS_PASSWORD
    REDIS_HOST

    SPARKPOST_API_KEY

    SECRET_FILE
    JWT_PRIVATE_KEY

    ZCONNECT_SENDER_ID
    ZCONNECT_SENDER_PASSWORD
    ZCONNECT_LISTENER_ID
    ZCONNECT_LISTENER_PASSWORD
    ZCONNECT_IBM_ORG

    GS_BUCKET_NAME
    GS_PROJECT_ID
    GS_SERVICE_ACCOUNT_FILENAME

    POSTGRES_HOST
    POSTGRES_USER
    POSTGRES_PASSWORD

Not required any more:

    POSTGRES_CA_CERT
    POSTGRES_CLIENT_CERT
    POSTGRES_CLIENT_KEY

REQUIRED files

    ${SECRET_FILE}
    ${JWT_PRIVATE_KEY}

    PROJECT_ROOT/keys/private.pem
    PROJECT_ROOT/keys/private.json
    PROJECT_ROOT/keys/${SECRET_FILE}

Not required any more:

    ${POSTGRES_CA_CERT}
    ${POSTGRES_CLIENT_CERT}
    ${POSTGRES_CLIENT_KEY}


"""
# pylint: disable=unused-wildcard-import, wildcard-import
# Python imports
from os import getenv
from os.path import abspath, dirname, join
import string

from google.oauth2 import service_account
import yaml

# project imports
from .common import *  # pylint: disable=unused-wildcard-import


def load_key(filename):
    """Load a file from KEY_ROOT"""
    return read_file_into_var(join(KEY_ROOT, "integration", filename))

STATIC_ROOT = "/django/run/static"

# uncomment the following line to include i18n
# from .i18n import *


# ##### DEBUG CONFIGURATION ###############################
DEBUG = False

# allow all hosts during development
ALLOWED_HOSTS = [
    "rtrzc2.olapi.io",
    "localhost",
]

# adjust the minimal login
LOGIN_URL = 'core_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'core_login'

CORS_ORIGIN_ALLOW_ALL = True

ZCONNECT_COMPONENT = getenv("ZCONNECT_COMPONENT", "unknown")


# ##### DATABASE CONFIGURATION ############################
DATABASES = {
    'default': {
        'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
        "NAME": "rtr-integration",
        'HOST': getenv("POSTGRES_HOST"),
        "USER": getenv("POSTGRES_USER"),
        "PASSWORD": read_file_from_env("POSTGRES_PASSWORD"),
        # 'ATOMIC_REQUESTS': False,
        'CONN_MAX_AGE': 0,
        "OPTIONS": {
            'MAX_CONNS': getenv("POSTGRES_MAX_CONNECTIONS", 2),
            "application_name": "rtr-django-integration-{}".format(ZCONNECT_COMPONENT),

            # This is now handled by could sql proxy
            # "sslcompression": True, # optional
            # "sslmode": "verify-ca",
            # "sslrootcert": getenv("POSTGRES_CA_CERT"),
            # "sslcert": getenv("POSTGRES_CLIENT_CERT"),
            # "sslkey": getenv("POSTGRES_CLIENT_KEY"),
        }
    }
}

REDIS = {
    "connection": {
        # "username": getenv("REDIS_USERNAME"),
        # "password": getenv("REDIS_PASSWORD"),
        # "password": read_file_from_env("REDIS_PASSWORD"),
        "host": getenv("REDIS_HOST"),
        "port": 6379,
    },
    "event_definition_evaluation_time_key": 'event_def_eval',
    "event_definition_state_key": 'event_def_state',
    # If an ev def hasn't been evaluated before, ev time will be set to
    # datetime.utcnow() + this offset.
    "event_definition_evaluation_time_clock_skew_offset": 5,
    "online_status_threshold_mins": 10,
}

CELERY_REDIS_HOST = REDIS["connection"]["host"]
CELERY_REDIS_PASSWORD = REDIS["connection"].get("password", None)
CELERY_REDIS_PORT = REDIS["connection"]["port"]
CELERY_BROKER_URL = "redis://{}".format(CELERY_REDIS_HOST)

# ##### APPLICATION CONFIGURATION #########################

INSTALLED_APPS = DEFAULT_APPS

REST_FRAMEWORK.update({
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
})

ZCONNECT_SETTINGS = {
    "SENDER_SETTINGS": {
        "cls": "zconnect.messages.IBMInterface",
        "auth-key": getenv("ZCONNECT_SENDER_ID"),
        "auth-token": read_file_from_env("ZCONNECT_SENDER_PASSWORD"),
        "org": getenv("ZCONNECT_IBM_ORG"),
        "type": "shared",
    },
    "LISTENER_SETTINGS": {
        "cls": "zconnect.messages.IBMInterface",
        "auth-key": getenv("ZCONNECT_LISTENER_ID"),
        "auth-token": read_file_from_env("ZCONNECT_LISTENER_PASSWORD"),
        "org": getenv("ZCONNECT_IBM_ORG"),
        "type": "shared",
        **DEFAULT_LISTENER_SETTINGS,
    },
}

ENABLE_STACKSAMPLER = True

# These need to be replaced when a service account is created for integration and production
GS_PROJECT_ID = getenv("GS_PROJECT_ID")

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    getenv("GS_SERVICE_ACCOUNT_FILENAME")
)

GS_BUCKET_NAME = getenv("GS_BUCKET_NAME")

here = dirname(abspath(__file__))

with open(join(here, "integration_logging.yaml")) as log_cfg_file:
    LOGGING = yaml.load(log_cfg_file)

df = string.Template(LOGGING["formatters"]["app_papertrail_fmt"]["format"])
df = df.safe_substitute(sysname=ZCONNECT_COMPONENT)
LOGGING["formatters"]["app_papertrail_fmt"]["format"] = df


########################### Email Configuration ###############################
EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'
# THIS API KEY IS FOR DEVELOPMENT ONLY!
SPARKPOST_API_KEY = read_file_from_env("SPARKPOST_API_KEY")

########################### SMS Configuration ###############################
SENDSMS_BACKEND = 'sendsms.backends.twiliorest.SmsBackend'
SENDSMS_TWILIO_ACCOUNT_SID = read_file_from_env("TWILIO_ACCOUNT_SID")
SENDSMS_TWILIO_AUTH_TOKEN = read_file_from_env("TWILIO_AUTH_TOKEN")

# ##### SECURITY CONFIGURATION ############################

# Redirects all requests to https
SECURE_SSL_REDIRECT = True

# Set an HSTS header. IF a browser sees an HSTS header, it will refuse to
# communicate non-securely with that domain for the given number of seconds.
# Note: currently set to 10 minutes as if there is in fact non-secure content
# served we may break that content.
# TODO: Once confirmed that everything is secured, change to something much
# bigger, e.g. 1 year
SECURE_HSTS_SECONDS = 600

# Session cookies will only be set, if https is used
SESSION_COOKIE_SECURE = True

# How long is a session cookie valid?
SESSION_COOKIE_AGE = 1209600

ADMINS = (
    ("Rich", "rich@zoetrope.io"),
    ("Ben", "ben@zoetrope.io"),
    ("Boulton", "boulton@zoetrope.io"),
)
MANAGERS = ADMINS

SIMPLE_JWT.update({
    "ALGORITHM": "RS256",
    "SIGNING_KEY": read_file_from_env("JWT_PRIVATE_KEY"),
    "VERIFYING_KEY": load_key("public.pem"),
})

SECRET_KEY = read_file_from_env("SECRET_FILE")

################################ EMAIL CONFIG ##################################

DEFAULT_FROM_EMAIL = "admin@zoetrope.io"

FRONTEND_PROTOCOL = 'https'
FRONTEND_DOMAIN = 'icontact.zconnect.io'

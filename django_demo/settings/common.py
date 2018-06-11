# Python imports
from os import getenv
from os.path import abspath, basename, dirname, join, normpath
import sys

from celery.schedules import crontab

# ##### PATH CONFIGURATION ################################

# fetch Django's project directory
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# fetch the project_root
PROJECT_ROOT = dirname(DJANGO_ROOT)

# the name of the whole site
SITE_NAME = basename(DJANGO_ROOT)

# collect static files here
STATIC_ROOT = join(PROJECT_ROOT, 'run', 'static')

# collect media files here
MEDIA_ROOT = join(PROJECT_ROOT, 'run', 'media')

KEY_ROOT = join(PROJECT_ROOT, "keys")

# look for static assets here
STATICFILES_DIRS = [
    join(PROJECT_ROOT, 'static'),
]

# look for templates here
# This is an internal setting, used in the TEMPLATES directive
PROJECT_TEMPLATES = [
    join(PROJECT_ROOT, 'templates'),
]

# add apps/ to the Python path
sys.path.append(normpath(join(PROJECT_ROOT, 'apps')))


# ##### APPLICATION CONFIGURATION #########################

# these are the apps
DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_auth",
    # "django_filters",
    "organizations",
    "guardian",
    "django_extensions",
    "rules.apps.AutodiscoverRulesConfig",
    "rest_framework_rules",
    "corsheaders",
    "phonenumber_field",
    "db_file_storage",

    "actstream",

    'zconnect',
    "zconnect.zc_billing",
    'zconnect.zc_timeseries',

    "django_demo",
]

# for django-activity-stream
SITE_ID = 1

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# template stuff
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': PROJECT_TEMPLATES,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

# Internationalization
USE_I18N = False

# For using 'fake' users?
# "REST_AUTH_TOKEN_MODEL": "rest_framework_simplejwt.models.TokenUser"
REST_AUTH_TOKEN_MODEL = "rest_framework_simplejwt.tokens.SlidingToken"
SIMPLE_JWT = {
    "AUTH_TOKEN_CLASSES": [
        REST_AUTH_TOKEN_MODEL,
    ]
}

REST_AUTH_SERIALIZERS = {
    # NOTE
    # Look at LoginView in django rest auth to see how this is used - This
    # should take a Token (from simplejwt, above) and serializer the response
    "TOKEN_SERIALIZER": "zconnect.serializers.TokenReturnSerializer",

    # NOTE
    # This serializer does the same as the 'default' one from django rest auth
    # (but validates slightly differently, so the error response is a bit
    # different). The only advantage of using this one is that it can be set up
    # so that it doesn't actually load the user from the database, and saves a
    # db access. It also gives a better error message if a field is missing.
    "LOGIN_SERIALIZER": "zconnect.serializers.TokenWithUserObtainSerializer",
}
REST_AUTH_TOKEN_CREATOR = "zconnect.serializers.jwt_create_token"

AUTHENTICATION_BACKENDS = [
    # Try to load a REST_AUTH_TOKEN_MODEL from the Bearer token in the
    # authorization header, then loads the user from the db.
    "rest_framework_simplejwt.authentication.JWTAuthentication",
    # The same, but returns the 'stateless' user - ie, not a real user
    # "rest_framework_simplejwt.authentication.JWTTokenUserAuthentication",
    # NOTE
    # Checking whether a user is authorized to do certain things can be done by
    # an auth backend
    # https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#handling-authorization-in-custom-backends
    # At the moment the plan is just to use django-guardian with permissions

    # Checks _Group_ based permissions
    "guardian.backends.ObjectPermissionBackend",

    # Is used to check _Organization_ based permissions
    "rules.permissions.ObjectPermissionBackend",

    # Basic model permissions
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


TIME_ZONE = "UTC"


# DEFAULT_CONTENT_TYPE = "application/json"
DEFAULT_CHARTSET = "utf-8"

REST_FRAMEWORK = {
    # Mostly used to disable the browseable API that rest_framework enables by
    # default
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        # "rest_framework.filters.DjangoObjectPermissionsFilter",
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # NOTE
        # See notes above
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    'DEFAULT_PAGINATION_CLASS': 'zconnect.pagination.StandardPagination',
    'PAGE_SIZE': 10,
}


DEFAULT_LISTENER_SETTINGS = {
    "worker_events_rate_limits": {
        "event": 100,
        "fw_update_complete": 100,
        "gateway_new_client": 100,
        "init_wifi_success": 100,
        "ir_receive_codes": 100,
        "ir_receive_codes_complete": 100,
        "local_ip": 100,
        "manual_status": 100,
        "periodic": 1000,
        "settings": 100,
        "version": 100,
        #for testing
        "rate_limiter_event": 1,
    },
    "rate_limit_period": 600,
}

ZCONNECT_DEVICE_MODEL = "django_demo.DemoDevice"
ZCONNECT_DEVICE_SERIALIZER = "django_demo.serializers.DemoDeviceSerializer"
ZCONNECT_JWT_SERIALIZER = "django_demo.serializers.DemoJWTUserSerializer"
ZCONNECT_USER_SERIALIZER = "django_demo.serializers.DemoUserSerializer"
ZCONNECT_ADMIN_USER_SERIALIZER = "django_demo.serializers.DemoAdminUserSerializer"
ZCONNECT_PRODUCT_SERIALIZER = "django_demo.serializers.DemoProductSerializer"
AUTH_USER_MODEL = 'zconnect.User'

# numpy or sql
# sql doesn't work in sqlite
ZCONNECT_TS_AGGREGATION_ENGINE = "numpy"

ORGS_SLUGFIELD = 'django_extensions.db.fields.AutoSlugField'

ACTSTREAM_SETTINGS = {
    'USE_JSONFIELD': True,
}

# Runtime profiling
ENABLE_STACKSAMPLER = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
FRONTEND_RESET_PASSWORD_CONFIRM_PATH = 'reset'

PHONENUMBER_DB_FORMAT = "INTERNATIONAL"
PHONENUMBER_DEFAULT_REGION = "GB"

# ##### SECURITY CONFIGURATION ############################

SECURE_REDIRECT_EXEMPT = [
    ".*stats/stacksampler.*"
]

# these persons receive error notification
ADMINS = (
    ('your name', 'your_name@example.com'),
)
MANAGERS = ADMINS

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# ##### DJANGO RUNNING CONFIGURATION ######################

# the default WSGI application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME

# the root URL configuration
ROOT_URLCONF = '%s.urls' % SITE_NAME

# the URL for static files
STATIC_URL = '/static/'

# the URL for media files
MEDIA_URL = '/media/'


# ##### CELERY CONFIGURATION ##############################

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# pickle throws big warnings about being unsafe
# json should be fine
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER='json'
CELERY_ACCEPT_CONTENT = ['json']

# Attempt to avoid memory leaks by restarting child processes after x tasks
CELERYD_MAX_TASKS_PER_CHILD = 20

CELERY_BEAT_SCHEDULE = {
    # Triggers once per minute
    "trigger_scheduled_events": {
        "task": "zconnect.tasks.trigger_scheduled_events",
        "schedule": crontab(minute='*')
    },
    "generate_all_outstanding_bills": {
        "task": "zconnect.zc_billing.tasks.generate_all_outstanding_bills",
        "schedule": crontab(hour=0)
    },
}

# Configure django-db-file-storage. See django-db-file-storage.readthedocs.io

DEFAULT_FILE_STORAGE = 'db_file_storage.storage.DatabaseFileStorage'


# ##### DEBUG CONFIGURATION ###############################
DEBUG = False


# Emails
SPARKPOST_OPTIONS = {
    'track_opens': False,
    'track_clicks': False,
    'transactional': True,
}


def read_file_into_var(filename, strip=True):
    """Open the file and return the contents, stripped of whitespace by default"""
    with open(filename, "r") as infile:
        return infile.read().strip()


def read_file_from_env(env_var):
    """Read a kubernetes secret file and return the contents

    In kubernetes, secrets are all stored in files and mounted into the
    container. For example, the django secret might be mounted at
    /mnt/django/SECRET_KEY - the location of this will be in an environment
    variable (eg ${DJANGO_SECRET_KEY_FILE_LOCATION}), then this function should be used
    to load it:

    .. code-block:: python

        SECRET_KEY = read_file_from_env("DJANGO_SECRET_KEY_FILE_LOCATION"))
    """
    return read_file_into_var(getenv(env_var))

#pylint: disable=unused-wildcard-import, wildcard-import

import uuid

from .development import *

# ##### DATABASE CONFIGURATION ############################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(PROJECT_ROOT, 'run', 'demo.sqlite3'),
    }
}

DATABASES["TEST"] = DATABASES["test"] = DATABASES["default"]

REDIS["connection"]["host"] = "redis"

CELERY_REDIS_HOST = REDIS["connection"]["host"]
CELERY_BROKER_URL = "redis://{}".format(REDIS["connection"]["host"])
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False


ZCONNECT_SETTINGS = {
    "SENDER_SETTINGS": {
        "cls": "zconnect.messages.IBMInterface",
        "type": "shared",

        "broker-url": "vernemq",
        "full_client_id": "g:abcdef:sender:123",
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
        "full_client_id": "g:abcdef:listener:125",
        "id": "test_sender",
        "disable-tls": True,
        "port": 1883,
        "auth-method": "token",
        "auth-key": "overlock-worker",
        "auth-token": "123456789",

        **DEFAULT_LISTENER_SETTINGS,
    },
}

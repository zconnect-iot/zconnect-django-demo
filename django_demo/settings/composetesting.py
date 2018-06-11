#pylint: disable=unused-wildcard-import, wildcard-import
from .composelocal import *

EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'
# THIS API KEY IS FOR DEVELOPMENT ONLY!
SPARKPOST_API_KEY = '609adece54b68c1d47857914bfbeada737c24676'

ZCONNECT_SETTINGS = {
    "SENDER_SETTINGS": {
        "cls": "zconnect.messages.IBMInterface",
        "auth-key": "a-s3lgr1-40bnpmt07q",
        "auth-token": "iqCn+AX7xxl)B9vKJ)",
        "org": "s31gr1",
        "type": "shared",
    },
    "LISTENER_SETTINGS": {
        "cls": "zconnect.messages.IBMInterface",
        "auth-key": "a-s3lgr1-i2kaoqdkxg",
        "auth-token": "d78hQ4n5LoYX?8vh2M",
        "org": "s31gr1",
        "type": "shared",
        **DEFAULT_LISTENER_SETTINGS,
    },
}

DEFAULT_FROM_EMAIL = "admin@zoetrope.io"
FRONTEND_PROTOCOL = 'https'
FRONTEND_DOMAIN = 'localhost:3000'

SENDSMS_TWILIO_ACCOUNT_SID = "AC280217602fd3dd358fd34d785f2b6472"
SENDSMS_TWILIO_AUTH_TOKEN = "8fcd2977d947a072a660e9e1227f7fa3"

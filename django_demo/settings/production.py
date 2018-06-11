# pylint: disable=unused-wildcard-import, wildcard-import

# for now fetch the development settings only
from .integration import *

# turn off all debugging
DEBUG = False

# You will have to determine, which hostnames should be served by Django
ALLOWED_HOSTS = []

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

# the email address, these error notifications to admins come from
# SERVER_EMAIL = 'root@localhost'

# how many days a password reset should work. I'd say even one day is too long
# PASSWORD_RESET_TIMEOUT_DAYS = 1

# dummy to stop linter complaining
SIMPLE_JWT.update({})


########################### SMS Configuration ###############################
SENDSMS_BACKEND = 'sendsms.backends.twiliorest.SmsBackend'
SENDSMS_TWILIO_ACCOUNT_SID = read_file_from_env("TWILIO_ACCOUNT_SID")
SENDSMS_TWILIO_AUTH_TOKEN = read_file_from_env("TWILIO_AUTH_TOKEN")

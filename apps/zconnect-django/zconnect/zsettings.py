"""Holds some settings that control the behaviour of the zconnect module

This shouldn't be edited directly, the settings in the app should override
these. Specify a dict called ZCONNECT_SETTINGS with values that can override the
things below

Settings:

Todo:
    https://github.com/encode/django-rest-framework/blob/master/rest_framework/settings.py
    django rest framework has a custom class and polls for settings updates -
    this is a bit complicated for the time being
"""

from django.conf import settings

# Should be a _dict_
overridden_settings = getattr(settings, "ZCONNECT_SETTINGS", {})

LISTENER_SETTINGS = overridden_settings.get("LISTENER_SETTINGS", {})
SENDER_SETTINGS = overridden_settings.get("SENDER_SETTINGS", {})


__all__ = [
    "SENDER_SETTINGS",
    "LISTENER_SETTINGS",
]

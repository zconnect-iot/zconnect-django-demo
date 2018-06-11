"""
WSGI config for django_demo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os # pylint: disable=wrong-import-position
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_demo.settings.production")

if os.getenv("DJANGO_SEED_PROJECT"):
    if os.getenv("DJANGO_SEED_REQUIRES_SETUP"):
        import django
        django.setup(set_prefix=False)
    from .seed import seed_project
    seed_project()

from django.core.wsgi import get_wsgi_application # pylint: disable=wrong-import-position
application = get_wsgi_application()

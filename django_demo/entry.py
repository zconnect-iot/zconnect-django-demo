"""Used for uwsgi"""
# pylint: disable=wrong-import-position

from gevent import monkey
monkey.patch_all()

from psycogreen.gevent import patch_psycopg
patch_psycopg()

from django_demo.wsgi import application # pylint: disable=unused-import

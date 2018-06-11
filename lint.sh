#!/bin/bash

pylama -o pytest.ini -l pep8 django_demo apps/zconnect-django
pylama -o pytest.ini -l pyflakes django_demo/tests apps/zconnect-django/tests
pylama -o pytest.ini -l pyflakes django_demo apps/zconnect-django/zconnect

pylint django_demo apps/zconnect-django/zconnect --rcfile .pylintrc
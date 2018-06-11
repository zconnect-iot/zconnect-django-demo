#!/bin/bash
set -ex

rm -f run/demo.sqlite3

./manage.py makemigrations zconnect django_demo zc_billing zc_timeseries
./manage.py migrate --run-syncdb

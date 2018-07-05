# zconnect-django-demo

`zconnect-django-demo` this is an example django application which uses `zconnect-django`, to see this as a part of a whole zconnect system please see https://github.com/zconnect-iot/demo-virtual-docker-compose

## Starting from scratch

1. `pip3 install --user pipenv` (if you don't already have it)
2. `pipenv install --dev`
3. `pipenv shell`
4. `./start.sh`

When done, run `deactivate` to close of the virtual env, or just close the terminal.

When coming back to do development, run `pipenv shell`

## Seed data

There is some seed data in `django_demo/seed.py` which is used if the environment
variable `DJANGO_SEED_PROJECT` is set when the server is started. This just
has some basic devices and timeseries data for now, it's just there as an
example and if you need anything extra then add it there.

Optionally you can set the environment variable `DJANGO_SEED_PROJECT_ONCE` as
well to stop the server from re-seeding the database every time the code
changes.

This data is also used in the `fix_Demo_ts_data` fixture, for example in the
dashboard endpoint tests.

By default it will only seed the database 'once', which means if it finds the
admin user already there it won't seed anything else. If you need to add more
seed data, do `docker volume prune` to delete all the old volumes and then run
the instructions above again

## Running celerybeat

To run the scheduled celery tasks you need to run the `worker` and the `beat`
with the following commands:

```
env DJANGO_SETTINGS_MODULE=django_demo.settings.development celery -A django_demo beat -l info
env DJANGO_SETTINGS_MODULE=django_demo.settings.development celery -A django_demo worker -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

However, the development settings set `CELERY_TASK_ALWAYS_EAGER` to `True` which
means that when running these commands locally, the `worker` will never recieve
the tasks. Instead, the `beat` will execute the tasks synchronously.

# Documentation

1. Go into virtualenv with all dev requirements installed
1. Go into `apps/zconnect-django/doc/source`
1. Run `make html`

The documentation will be output in the `build/html` folder.

# Tests

## Running unit tests

(maybe pip install -r requirements.txt)
1. `pipenv shell`
2. `py.test -c pytest.ini -k .py` (-k deselects the tavern tests)

NB: The fixture `fake_get_redis` has autouse set to True, so any uses of `get_redis` in `zconnect.tasks` will return a Mocked version of redis, this is to avoid the need to run a redis-server during unit tests.

## Linting

To recreate the linting that happens in GitLab CI, run `./lint.sh`. Aim to do this before every push, so that you don't push, wait for tests and realise that you missed something trivial and have to repeat the process!

You can also run `./pylint.sh` for just pylint.


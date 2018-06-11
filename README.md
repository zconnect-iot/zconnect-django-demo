# Starting from scratch

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

## v1 import
To import v1 timeseries data (along with product, sensors, groups, devices, and
device sensors) run command:
`./manage.py v1_import`
There have been cases where the mongo command to export data from the v1
database does not work, if this is the case add the flag `--kwak` to execute the
mongo command from kwak.

To remove when this is no longer needed:
- Paramiko dependency
- v1 import command

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

# Using docker compose with postgres

1. `docker-compose -f docker-compose-postgres.yaml build`
2. `docker-compose -f docker-compose-postgres.yaml up database`
3. In another terminal: `./deploy/init_postgres.sh` (You will need a postgres client installed, e.g. `sudo apt-get install postgresql-client`)
4. Stop docker-compose
5. `docker-compose -f docker-compose-postgres.yaml up`

## Seeding

By default it will only seed the database 'once', which means if it finds the
admin user already there it won't seed anything else. If you need to add more
seed data, do `docker volume prune` to delete all the old volumes and then run
the instructions above again

# Documentation

1. Go into virtualenv with all dev requirements installed
1. Go into `apps/zconnect-django/doc/source`
1. Run `make html`

The documentation will be output in the `build/html` folder.

# Tests
## Integration tests

1. `docker-compose -f docker-compose-tavern.yaml build`
2. `docker-compose -f docker-compose-tavern.yaml run tavern`

## Running unit tests

(maybe pip install -r requirements.txt)
1. `pipenv shell`
2. `py.test -c pytest.ini -k .py` (-k deselects the tavern tests)

NB: The fixture `fake_get_redis` has autouse set to True, so any uses of `get_redis` in `zconnect.tasks` will return a Mocked version of redis, this is to avoid the need to run a redis-server during unit tests.

## Linting

To recreate the linting that happens in GitLab CI, run `./lint.sh`. Aim to do this before every push, so that you don't push, wait for tests and realise that you missed something trivial and have to repeat the process!

You can also run `./pylint.sh` for just pylint.

# Connecting to the database
The postgresql database is hosted on google cloud.

To connect directly requires quite a few private keys etc, which you probably don't want to be storing on your computer.
To avoid this, we use google's cloud-sql-proxy.

This requires installing `cloud-sql-proxy` and `google-cloud-sdk` as per the documentation:

https://cloud.google.com/sql/docs/mysql/sql-proxy#install

https://cloud.google.com/sdk/downloads

Once installed, you'll need to login to the cloud sdk with the following commands:

```
gcloud auth application-default login
```

This will open a browser window where you can authenticate. Use the google account that has access to the google cloud project.

Then set the project using:

```
gcloud config set project zconnect-201710
```

You can then attempt to connect to the google cloud sql proxy instance:

```
cloud-sql-proxy -instances=zconnect-201710:europe-west2:demo-integration-postgres=tcp:15432
```

Here we are creating a proxy on port 15432. Unix sockets can also be used, however there is a path length restriction in some clients which is difficult to work with.

You can then connect to `localhost:15432` with a postgresql client e.g. pgadmin4 using a valid username and password for the postgres db.

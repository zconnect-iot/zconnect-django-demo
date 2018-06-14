FROM python:3.5-slim-jessie as builder
ARG DJANGOVER=2.0.5

RUN apt-get update && apt-get install build-essential git --yes --no-install-recommends # && apt-get clean --yes
RUN pip3 install --upgrade pip setuptools wheel

RUN mkdir /zconnect /install

COPY requirements/base.txt \
     apps/zconnect-django/setup.py \
     apps/zconnect-django/setup.cfg \
     /zconnect/

COPY apps/zconnect-django/zconnect/ /zconnect/zconnect/

RUN pip3 install \
        -r /zconnect/base.txt \
        django==$DJANGOVER \
        /zconnect/ \
        --prefix=/install
        # --install-option="--prefix=/install"


FROM python:3.5-slim-jessie
ENV PYTHONUNBUFFERED 1

RUN adduser --system --disabled-password --gecos '' --uid 401 worker_user
RUN mkdir -p /django /django/run /secrets
RUN chown worker_user /django/run /secrets

COPY --from=builder /install /usr/local

COPY requirements/development.txt /
RUN pip3 install -r development.txt

COPY manage.py /django
COPY configs /django/configs
COPY keys /django/keys

COPY django_demo /django/django_demo
COPY static /django/static
COPY templates /django/templates
RUN PYTHONPATH=/django DJANGO_SETTINGS_MODULE=django_demo.settings.development django-admin collectstatic --noinput && mv /django/run/static /www

USER worker_user

# CMD ["python3", "/django/manage.py", "runserver", "0.0.0.0:8981"]
# CMD ["celery", "-A", "django_demo", "worker", "-l", "info"]
# CMD ["uwsgi", "--ini", "/django/configs/uwsgi-listener-development.ini"]

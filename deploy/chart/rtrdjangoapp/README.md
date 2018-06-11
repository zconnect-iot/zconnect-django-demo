# Versioning

This folder has a separate bumpversion config which will bump the version of the
chart and not the version of the software. It's not intended for anyone to bump
the version of the chart with `--tag`, and if you do it will create a tag with a
different name.

# Template files

Worth explaining because it's a bit complicated (also see the official chart
repository for a lot more examples https://github.com/kubernetes/charts)

This is for the `api-deployment.yaml` which has the most stuff in it, but the
other ones are very similar.

```yaml
spec:
  volumes:
  - name: secret-volume
    secret:
      secretName: {{ required "secrets::file_secret_name is requred" .Values.secrets.file_secret_name }}
      defaultMode: 256
  - name: static-volume
    emptyDir:
      medium: Memory
  - name: key-volume
    emptyDir:
      medium: Memory
```

- Secret volume is mounted from the secrets stored in whatever the secret is
  named - this will be a key:value store of filename: contents of file, which
  are then mounted as files into this volume, using mode `0400`. This is here as
  `256` because the chart is converted to json and it can't handle octal numbers
  (400 oct = 256 dec)

- Static volume is used to serve the static data - this is served by uwsgi. This
  might be out of data because it's a silly way of doing it, this will probably
  get changed to just serve static data from a nginx container (and might
  already be if you are reading this)

- Key volume is just used to store the postgres client key - see below for
  details

The last two are done in memory just because it's slightly faster. This uses
more memory on the kubernetes host, but it's in the order of 500KB.


```yaml
  securityContext:
    fsGroup: 2000
```

Run all pods with filesystem group 2000 - this allows them to read the secrets
which are mounted as being owned by root with mode `0400`


```yaml
  initContainers:
  - name: chown-secrets
    image: debian:jessie-slim
    command:
    - sh
    - -c
    - "set -ex; cp ${POSTGRES_CLIENT_KEY_ORIG} ${POSTGRES_CLIENT_KEY}; chmod 0400 ${POSTGRES_CLIENT_KEY}; chown 401 ${POSTGRES_CLIENT_KEY}; "
    envFrom:
    - configMapRef:
        name: {{ .Release.Name }}-{{ .Values.global_config.name }}
    volumeMounts:
    - name: secret-volume
      readOnly: true
      mountPath: /secrets
    - name: key-volume
      mountPath: /postgres
```

Postgres (or more accurately psycopg2) will fail if the client private key
is not restricted so it can only be read by the current user. Because we don't
want to run inside the containers using root, this means we need to copy the
private key then change ownership and the file mode so only the user running
inside the container can read it. In the docker file, the user is created
specifically using uid 401, hence the `chown 401`.


```yaml
  - name: generate-static-files
    image: {{ required "A valid image must be specified!" .Values.api.deployment.container.image }}:{{ .Chart.AppVersion }}
    command:
    - /usr/local/bin/django-admin
    - collectstatic
    - --noinput
    envFrom:
    - configMapRef:
        name: {{ .Release.Name }}-{{ .Values.global_config.name }}
    volumeMounts:
    - name: secret-volume
      readOnly: true
      mountPath: /secrets
    - name: key-volume
      mountPath: /postgres
    - name: static-volume
      mountPath: /django/run/static
```

Generates static files and puts them in `/django/run/static`. The uwsgi config
serves everything on `/static` by reading it from this directory. This is
obviously a bit silly to do all the time in every container and should be
changed. (*To be removed*)[https://code.zoetrope.io/RTR-services/rtr-django-app/issues/54].


```yaml
  containers:
  - name: {{ template "name" . }}-api
    image: {{ required "A valid image must be specified!" .Values.api.deployment.container.image }}:{{ .Chart.AppVersion }}
    env:
    - name: ZCONNECT_COMPONENT
      value: "api-server"
```

`ZCONNECT_COMPONENT` is used just for logging, so that it shows up in
papertrail as being logged from the api server, or the celery runner, etc.

*Note*: This uses `.Chart.AppVersion` rather than `.Chart.Version` because it
refers to the version of the CODE, not the version of the CHART, which are
tracked separately.

```yaml
    envFrom:
    - configMapRef:
        name: {{ .Release.Name }}-{{ .Values.global_config.name }}
```

Everything from the `global_config` configmap is loaded as environment
variables. This is similar to how the secrets are mounted as files.

```yaml
    volumeMounts:
    - name: secret-volume
      readOnly: true
      mountPath: /secrets
    - name: key-volume
      mountPath: /postgres
    - name: static-volume
      mountPath: /django/run/static
```

All the other volumes required with secrets, static content, and postgres key

```yaml
    ports:
    - name: server-port
      containerPort: !!int {{ .Values.api.service.port }}
```

Which port is exposed to the pod. This should be the same as the one that uwsgi
is serving on, and the same as the one that the service is using as it's
`targetPort`.

```yaml
{{- if .Values.api.deployment.container.command }}
    command:
{{ .Values.api.deployment.container.command | toYaml | indent 10 }}
{{- end }}
```

Possibly override container command. We currently just use one container with
the same code and run a different command in each of them.

```yaml
    resources:
{{ toYaml .Values.api.deployment.resources | indent 10 }}
```

Need to specify resources otherwise GKE assumes that every container requires
100% CPU - by default this just assumes they only need 10% of a CPU and 128MB
minimum

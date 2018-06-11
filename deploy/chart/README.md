# Setting up database

1. Create the database via google cloud SQL (postgres!)

2. Create the user that the app will connect to the database with (eg `django`)

3. Create the database in question (eg `rtr-integration`) with the owner being
the user you just created

4. Create any supplemental users that should have access (read only by default)

5. Create a new service account in the google cloud console with the permissions
as specified (in the docs)[https://github.com/kubernetes/charts/tree/master/stable/gcloud-sqlproxy#installing-the-chart]
and get the service account key for later

# Deploying app

1. Set up the cluster - [instructions here](https://code.zoetrope.io/zconnect/helm-deployment-start)

2. Create a secret with all the required files in. A list of them should be kept
up to date in values.yaml, or the settings files. The easiest way to do this is:

 1. Put them all in the secrets/ folder (where everything will be gitignored)
 with the names expected in the environemnt values file - for example,
 integration.yaml requires `/secrets/postgres-client-key.pem`, so copy the
 potgres client key from lastpass and put in a file called
 `postgres-client-key.pem`.

 2. Create a secret from these files - I did it with `kubectl create secret generic rtr-integration-secrets --from-file=secrets`

 3. Put the name of this secret into `secrets::file_secret_name` in the
 environment values file.

3. Update all the other settings - a list of required ones is in values.yaml/the
settings files (eg `GS_PROJECT_ID`)

4. Build containers and push to repo

5. Deploy with helm as usual, but specify the privatekey on the command line as
specified (in the docs)[https://github.com/kubernetes/charts/tree/master/stable/gcloud-sqlproxy#installing-the-chart]
for example:

```shell
helm install rtrdjangoapp/ --values integration.yaml \
    --set gcloud-sqlproxy.serviceAccountKey="$(cat service-account.json | base64 --wrap=0)"
```

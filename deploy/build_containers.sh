#!/bin/sh

set -ex

CI_COMMIT_TAG=0.7.4
GCR_REGISTRY_PREFIX=eu.gcr.io
GCLOUD_PROJECT_NAME=zconnect-201710

REMOTE_IMAGE_NAME="${GCR_REGISTRY_PREFIX}/${GCLOUD_PROJECT_NAME}/rtrdjangoapp:${CI_COMMIT_TAG}"

docker build -f deploy/Dockerfile -t ${REMOTE_IMAGE_NAME} .

docker push ${REMOTE_IMAGE_NAME}

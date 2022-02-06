#!/bin/sh

cd /app

FLASK_CACHE_SIZE=${FLASK_CACHE_SIZE:-256}
FLASK_SESSION_FILE_DIR=${FLASK_SESSION_FILE_DIR:-/tmp/sessions}

if [ ! -z "${FLASK_DEBUG}" ]; then
    UWSGI_ARGS="--py-autoreload=1"
fi

mkdir -p ${FLASK_SESSION_FILE_DIR}
chown nobody:nobody $(dirname ${FLASK_DB_PATH})
chown nobody:nobody ${FLASK_SESSION_FILE_DIR}

uwsgi --enable-threads --http=${FLASK_HOST}:${FLASK_PORT} \
      --uid=65534 --gid=65534 --cache2 name=default,items=${FLASK_CACHE_SIZE} \
      --manage-script-name --mount /=api.wsgi:app ${UWSGI_ARGS}

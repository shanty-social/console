#!/bin/sh

cd /app

FLASK_CACHE_SIZE=${FLASK_CACHE_SIZE:-256}
FLASK_SESSION_FILE_DIR=${FLASK_SESSION_FILE_DIR:-/tmp/sessions}
FLASK_DB_PATH=${FLASK_DB_PATH:-/tmp/db.sqlite3}
FLASK_HOST=${FLASK_HOST:-0.0.0.0}
FLASK_PORT=${FLASK_PORT:-8000}

if [ ! -z "${FLASK_DEBUG}" ]; then
    UWSGI_ARGS="--py-autoreload=1"
fi

if [ "${START_COMPOSE}" == "yes" ]; then
    docker-compose -p system -f /app/docker-compose.yml up -d
fi

mkdir -p ${FLASK_SESSION_FILE_DIR}
chown nobody:nobody $(dirname ${FLASK_DB_PATH})
chown nobody:nobody ${FLASK_SESSION_FILE_DIR}

uwsgi --enable-threads --http=${FLASK_HOST}:${FLASK_PORT} \
      --uid=65534 --gid=65534 --cache2 name=default,items=${FLASK_CACHE_SIZE} \
      --http-websockets --gevent 1000 --manage-script-name \
      --mount /=api.wsgi:app ${UWSGI_ARGS} \
      --static-map /assets=/app/assets --static-map /=/app/assets \
      --static-index=index.html --static-gzip-all

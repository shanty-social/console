#!/bin/sh

cd /app

FLASK_CACHE_SIZE=${FLASK_CACHE_SIZE:-256}

if [ ! -z "${FLASK_DEBUG}" ]; then
    UWSGI_ARGS="--py-autoreload=1"
fi

chown nobody:nobody $(dirname ${FLASK_DB_PATH})

uwsgi --enable-threads --http=${FLASK_HOST}:${FLASK_PORT} \
      --uid=65534 --gid=65534 --cache2 name=default,items=${FLASK_CACHE_SIZE} \
      --manage-script-name --mount /=api.wsgi:app ${UWSGI_ARGS}

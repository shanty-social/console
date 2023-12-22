#!/bin/sh

cd /app

PUID=${PUID:-1000}
PGID=${PGID:-1000}
FLASK_CACHE_SIZE=${FLASK_CACHE_SIZE:-256}
FLASK_SESSION_FILE_DIR=${FLASK_SESSION_FILE_DIR:-/tmp/sessions}
FLASK_DB_PATH=${FLASK_DB_PATH:-/tmp/db.sqlite3}
FLASK_HOST=${FLASK_HOST:-0.0.0.0}
FLASK_PORT=${FLASK_PORT:-8000}
COMPOSE_PATH=${COMPOSE_PATH:-/app/docker-compose.yml}

create_secret() {
    local path=${1}

    if [ -f ${path} ]; then
        return 0
    fi

    mkdir -p $(dirname ${path})
    tr -dc a-Za-z0-9 < /dev/urandom | head -c 64 > ${path}
}

create_secrets() {
    grep file: ${COMPOSE_PATH} | awk ' { print $2 } ' | \
    while read path; do
        create_secret ${path}
    done
}

if [ ! -z "${COMPOSE_PATH}" ]; then
    create_secrets
    docker-compose -p system -f ${COMPOSE_PATH} up -d
fi

if [ ! -z "${FLASK_DEBUG}" ]; then
    UWSGI_ARGS="--py-autoreload=1"
fi

mkdir -p ${FLASK_SESSION_FILE_DIR}
mkdir -p $(dirname ${FLASK_DB_PATH})
chown ${PUID}:${PGID} $(dirname ${FLASK_DB_PATH})
chown ${PUID}:${PGID} ${FLASK_SESSION_FILE_DIR}

uwsgi --enable-threads --http=${FLASK_HOST}:${FLASK_PORT} \
      --uid=${PUID} --gid=${PGID} --cache2 name=default,items=${FLASK_CACHE_SIZE} \
      --http-websockets --gevent 1000 --manage-script-name \
      --mount /=api.wsgi:app ${UWSGI_ARGS} \
      --static-map /assets=/app/assets --static-map /=/app/assets \
      --static-index=index.html --static-gzip-all
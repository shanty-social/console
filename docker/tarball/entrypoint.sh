#!/bin/sh -x

DOCKER_STORE=/var/lib/docker
DOCKER_PID=$(pidof dockerd)

if [ ! -z "${DOCKER_PID}" ]; then
    kill ${DOCKER_PID}
fi
rm -rf ${DOCKER_STORE}/*

# Use docker to pull image then make tarball.
/usr/local/bin/dockerd --experimental --storage-driver vfs \
                       --data-root "${DOCKER_STORE}" > /dev/null 2>&1 &
DOCKER_PID=$!
sleep 5
/usr/local/bin/docker --host unix:///var/run/docker.sock pull --platform=${ARCH} shantysocial/console:latest

rm -rf "${DOCKER_STORE}/runtimes"
rm -rf "${DOCKER_STORE}/tmp"

kill ${DOCKER_PID}
sleep 3

tar czf ${OUTPUT} ${DOCKER_STORE}
chown ${UID}:${GID} ${OUTPUT}

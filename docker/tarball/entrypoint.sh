#!/bin/sh -x

DOCKER_STORE=/var/lib/docker

kill $(pidof dockerd)
rm -rf ${DOCKER_STORE}

# Use docker to 
/usr/local/bin/dockerd --storage-driver vfs --data-root "${DOCKER_STORE}" > /dev/null 2>&1 &
DOCKER_PID=$!
sleep 5
/usr/local/bin/docker --host unix:///var/run/docker.sock pull --platform=${ARCH} shantysocial/console:latest

rm -rf "${DOCKER_STORE}/runtimes"
rm -rf "${DOCKER_STORE}/tmp"

kill ${DOCKER_PID}

cd ${DOCKER_STORE}
tar czf ${OUTPUT} *
chown ${UID}:${GID} ${OUTPUT}

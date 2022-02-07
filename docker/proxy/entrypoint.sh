#!/bin/sh -x

configure() {
    if [ ! -f "${PID}" ] || ! kill -0 $(cat ${PID}); then
        nginx -g 'daemon off;' &
        echo -n "$!" > ${PID}
    else
        kill -HUP $(cat ${PID})
    fi
}

trap 'configure' 1

while true; do
    configure
    sleep 300
done

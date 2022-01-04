#!/bin/sh

start_wpa() {
    # Start wpa_supplicant
    wpa_supplicant -i${INTERFACE} -Dnl80211 \
                -c/etc/wpa_supplicant/wpa_supplicant.conf &
    WPA_PID=$!
}

start_dhcp() {
    dnsmasq --port=0 --interface=${INTERFACE} --dhcp-authoritative \
            --address=${ADDRESS} \
            --dhcp-range=${DHCP_RANGE} --dhcp-option=1,255.255.255.0 \
            --dhcp-option=3 --dhcp-option=6 \
            --log-dhcp --log-debug --log-facility=- &
    DHCP_PID=$!
}

ifdown() {
    ifconfig ${INTERFACE} down
}

ifconfig ${INTERFACE} ${ADDRESS} netmask 255.255.255.0 up
trap ifdown EXIT

start_dhcp
start_wpa

while true; do
    sleep 3
    for PID in ${WPA_PID} ${DHCP_PID}; do
        if kill -0 ${PID} > /dev/null 2>&1 ; then
            # continue the OUTER loop (while true)
            continue 2
        fi
    done
    # IF here all pids are dead.
    echo All pids dead, exiting...
    break
done

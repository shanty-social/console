#!/bin/sh

start_wpa() {
    # Start wpa_supplicant
    WPA_CONF=/etc/wpa_supplicant/wpa_supplicant.conf
    envsubst < ${WPA_CONF}.tmpl > ${WPA_CONF}
    wpa_supplicant -i${INTERFACE} -Dnl80211 -c${WPA_CONF} | \
        grep -v CTRL-EVENT-SCAN-FAILED 2>&1 &
    WPA_PID=$!
}

start_dhcp() {
    # Start dnsmasq for DHCP
    dnsmasq --port=0 --interface=${INTERFACE} --dhcp-authoritative \
            --address=${ADDRESS} \
            --dhcp-range=${DHCP_RANGE} --dhcp-option=1,255.255.255.0 \
            --dhcp-option=3 --dhcp-option=6 \
            --log-dhcp --log-debug --log-facility=- &
    DHCP_PID=$!
}

start_nds() {
    local NDS_CONF=/etc/nodogsplash/nodogsplash.conf
    envsubst < ${NDS_CONF}.tmpl > ${NDS_CONF}
    nodogsplash -f -c ${NDS_CONF} -w ${NDS_SOCKET_PATH} &
    NDS_PID=$!
}

ifup() {
    ifconfig ${INTERFACE} ${ADDRESS} netmask 255.255.255.0 up

    # Redirect all traffic from wifi interface to the web interface.
    #iptables -t nat -A PREROUTING -p tcp -i ${INTERFACE} -j DNAT --to-destination ${ADDRESS}:8000
    #iptables -t nat -A POSTROUTING -j MASQUERADE
}

ifdown() {
    ifconfig ${INTERFACE} down
}

ifup
trap ifdown EXIT
start_nds
start_dhcp
start_wpa

while true; do
    sleep 3
    for PID in ${WPA_PID} ${DHCP_PID} ${DNS_PID}; do
        if kill -0 ${PID} > /dev/null 2>&1 ; then
            # continue the OUTER loop (while true)
            continue 2
        fi
    done

    # IF here all pids are dead.
    echo All pids dead, exiting...
    break
done

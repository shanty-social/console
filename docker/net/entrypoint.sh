#!/bin/sh

# Some defaults:
APD_CHANNEL=${APD_CHANNEL:-6}

del_uap0() {
    # Stop services
    kill ${WPA_PID} ${APD_PID} ${DHCP_PID} > /dev/null 2>&1

    # Remove apd interface when script exits.
    ifconfig uap0 down
    iw dev uap0 del
}

add_uap0() {
    # Configure apd interface.
    iw phy phy1 interface add uap0 type __ap
    #ifconfig uap0 ${ADDRESS} netmask 255.255.255.0 up
    #ifconfig uap0
}

start_wpa() {
    # Start wpa_supplicant
    wpa_supplicant -i${INTERFACE} -Dnl80211 \
                -c/etc/wpa_supplicant/wpa_supplicant.conf &
    WPA_PID=$!
}

start_apd() {
    # Start hostapd
    cat << EOF | hostapd -g /var/run/hostapd/control -G nobody /dev/stdin &
interface=${INTERFACE}
ssid=${APD_SSID}
hw_mode=g
channel=${APD_CHANNEL}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=${APD_PASSPHRASE}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF
    APD_PID=$!
}

start_dhcp() {
    dnsmasq --port=0 --interface=${INTERFACE} --dhcp-authoritative \
            --dhcp-range=${DHCP_RANGE} --dhcp-option=1,255.255.255.0 \
            --dhcp-option=3 --dhcp-option=6 &
    DHCP_PID=$!
}

#add_uap0
#trap del_uap0 EXIT
#start_apd
#sleep 3
start_dhcp
start_wpa
#ifconfig uap0 ${ADDRESS} netmask 255.255.255.0 up

while true; do
    sleep 3
    for PID in ${WPA_PID} ${APD_PID} ${DHCP_PID}; do
        if kill -0 ${PID} > /dev/null 2>&1 ; then
            # continue the OUTER loop (while true)
            continue 2
        fi
    done
    # IF here all pids are dead.
    echo All pids dead
    break
done

FROM ${ARCH}alpine:3.15

ADD docker/net/entrypoint.sh /entrypoint.sh
ADD docker/net/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

RUN chmod +x /entrypoint.sh && \
    apk add --no-cache wpa_supplicant dnsmasq iptables

WORKDIR /

VOLUME /var/run/wpa_supplicant
VOLUME /var/run/hostapd

ENTRYPOINT [ "/entrypoint.sh" ]

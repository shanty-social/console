ARG ALPINE_VERSION=3.18

FROM ${ARCH}alpine:${ALPINE_VERSION}

ADD ./docker/net/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Python
WORKDIR /app
RUN apk add --no-cache bridge hostapd wireless-tools wpa_supplicant \
                       dnsmasq iw ethtool websocat

ENTRYPOINT [ "/entrypoint.sh" ]

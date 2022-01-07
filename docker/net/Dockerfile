FROM ${ARCH}alpine:3.15

RUN apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/ envsubst && \
    apk add --no-cache build-base git linux-headers libmicrohttpd \
                       libmicrohttpd-dev wpa_supplicant dnsmasq iptables && \
    git clone https://github.com/nodogsplash/nodogsplash.git && \
    cd nodogsplash && \
    make && \
    make install  && \
    apk del build-base git linux-headers libmicrohttpd-dev

ADD docker/net/entrypoint.sh /entrypoint.sh
ADD docker/net/wpa_supplicant.conf.tmpl /etc/wpa_supplicant/wpa_supplicant.conf.tmpl
ADD docker/net/nodogsplash.conf.tmpl /etc/nodogsplash/nodogsplash.html.tmpl
ADD docker/net/splash.html /etc/nodogsplash/htdocs/splash.html

RUN chmod +x /entrypoint.sh

WORKDIR /

ENTRYPOINT [ "/entrypoint.sh" ]

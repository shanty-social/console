FROM docker:dind

ENV UID=1000
ENV GID=1000
ENV OUTPUT=/output/var-lib-docker.tgz

ADD docker/tarball/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]

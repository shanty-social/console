FROM ${ARCH}alpine:3.15 AS python

ARG DOCKER_GID=130
ARG CERT_DIR=/var/lib/certs
ENV CERT_DIR=${CERT_DIR}
ENV MKP224O_TAG=v1.5.0

# Add the python application, be sure to exclude dotfiles.
ADD ./back/api /app/
ADD ./back/Pipfile* /app/
ADD ./docker/console/entrypoint-app.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Python
WORKDIR /app
RUN apk add --no-cache linux-headers build-base python3 py3-pip py3-cryptography \
                                     python3-dev git libsodium libsodium-dev autoconf \
                                     libffi libffi-dev musl-dev pcre2 pcre2-dev openssl openssl-dev && \
    pip install wheel pipenv && \
    pipenv install --system --skip-lock && \
    mkdir -p /usr/local/src && cd /usr/local/src && \
    git clone --branch ${MKP224O_TAG} https://github.com/cathugger/mkp224o.git && cd mkp224o && \
    ./autogen.sh && ./configure --enable-regex=yes && \
    make && install mkp224o /usr/local/bin/mkp224o && \
    cd / && rm -rf /usr/local/src && \
    apk del build-base python3-dev git libsodium-dev autoconf pcre2-dev libffi-dev musl-dev openssl-dev && \
    addgroup -g ${DOCKER_GID} docker && \
    adduser nobody docker && \
    mkdir ${CERT_DIR} && \
    chown -R nobody:nobody ${CERT_DIR}

ENTRYPOINT [ "/entrypoint.sh" ]

FROM python AS node

ADD ./docker/console/entrypoint-vue.sh /entrypoint.sh
ADD ./front /front
RUN chmod +x /entrypoint.sh

# Install Node
WORKDIR /front
RUN apk add --no-cache nodejs npm && \
    npm i

ENTRYPOINT [ "/entrypoint.sh" ]

FROM node AS build

# Build vue application.
WORKDIR /front
RUN npm run build

FROM python AS final

# Copy vue static files.
COPY --from=build /front/dist/static /app/static
COPY --from=build /front/dist/index.html /app/templates/

USER nobody

WORKDIR /app

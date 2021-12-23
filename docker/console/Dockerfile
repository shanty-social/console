FROM ${ARCH}alpine:3 AS python

# Add the python application.
ADD ./back /app
ADD ./docker/console/entrypoint-app.sh /entrypoint.sh

# Install Python
WORKDIR /app
RUN apk add --no-cache alpine-sdk python3 py3-pip python3-dev && \
    pip install pipenv setuptools && \
    pipenv install --system && \
    pip uninstall -y pipenv && \
    apk del py3-pip alpine-sdk python3-dev

ENTRYPOINT [ "/entrypoint.sh" ]

FROM python AS node

ADD ./docker/console/entrypoint-vue.sh /entrypoint.sh
ADD ./front /front

# Install Node
WORKDIR /front
RUN apk add --no-cache nodejs npm && \
    npm i

FROM node AS build

# Build vue application.
WORKDIR /front
RUN npm run build

FROM python AS final

# Copy vue static files.
COPY --from=build /front/dist/static /app/static
COPY --from=build /front/dist/index.html /app/templates/

WORKDIR /app

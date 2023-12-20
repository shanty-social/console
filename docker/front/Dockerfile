FROM node:21-alpine3.18 AS node

ADD ./front /front

WORKDIR /front
ENV NODE_OPTIONS=--openssl-legacy-provider
RUN npm i
RUN npm run build

ENTRYPOINT [ "npm", "run", "serve" ]

FROM scratch AS final

COPY --from=node /front/dist /app

VOLUME /app

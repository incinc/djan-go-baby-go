FROM node:26-trixie-slim

WORKDIR /opt

COPY package.json package.json
COPY package-lock.json package-lock.json

ENV PATH="/opt/node_modules/.bin:${PATH}"

RUN npm ci

WORKDIR /opt/src

FROM node:23-bookworm-slim

WORKDIR /opt

COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm install

WORKDIR /opt/src

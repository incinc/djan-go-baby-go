FROM node:21-bullseye-slim

WORKDIR /opt

COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm install

WORKDIR /opt/src

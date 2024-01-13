#!/usr/bin/env bash

args=("$@")
PROJECT="$args[1]"

cp ./.env.example ./.env
echo "SECRET_KEY=\"$(head -c 64 /dev/urandom | base64 -w0)\"" >> .env

mv mynewapp "$PROJECT"
find ./ -type f -exec sed -i "s/mynewapp/$PROJECT/gI" {} \;

docker compose build
docker compose up

docker compose exec web python3 bash -c \
    "python3 manage.py makemigrations && python3 manage.py migrate"


#!/usr/bin/env bash


generate_secret() {
    shuf -er -n"$1" {A..Z} {a..z} {0..9} | tr -d '\n'
}

PROJECT="$1"
echo "Bootstrapping as '$PROJECT'"

if [ ! -f "./.env" ]; then
    export POSTGRES_PASSWORD="$(generate_secret 20)"
    export SECRET_KEY="$(generate_secret 128)"
    envsubst < .env.tmpl > .env
fi

if [ ! -d "$PROJECT" ]; then
    mv gobabygo "$PROJECT"
fi

find ./ -type f -exec sed -i "s/gobabygo/$PROJECT/gI" {} \;

docker compose build
docker compose run web bash -c \
    "python3 manage.py makemigrations && python3 manage.py migrate"
docker compose up

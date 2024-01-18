#!/usr/bin/env bash


generate_secret() {
    shuf -er -n"$1" {A..Z} {a..z} {0..9} | tr -d '\n'
}

PROJECT="$1"

valid_python_identifier='^[a-zA-Z0-9_]+$'

if ! [[ $PROJECT =~ $valid_python_identifier ]]; then
    echo "$PROJECT is not a valid Python identifier. Only alphanumeric characters and underscores are allowed."
    exit 1
fi

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

docker compose build --build-arg uid=$(id -u) --build-arg gid=$(id -g)
docker compose run web bash -c \
    "python3 manage.py makemigrations && python3 manage.py migrate"
docker compose up "$2"

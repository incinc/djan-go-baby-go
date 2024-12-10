#!/usr/bin/env sh

# Ensure Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required but not installed. Please install Docker first."
    exit 1
fi

PROJECT="$1"

if [ -z "$PROJECT" ]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

# Run the bootstrap process in a container
docker run --rm -v "$(pwd):/work" -w /work alpine:3.18 sh -c "
    # Install required tools
    apk add --no-cache gettext

    # Validate project name
    if ! echo '$PROJECT' | grep -qE '^[a-zA-Z0-9_]+$'; then
        echo '$PROJECT is not a valid Python identifier. Only alphanumeric characters and underscores are allowed.'
        exit 1
    fi

    echo 'Bootstrapping as $PROJECT'

    # Generate secrets and create .env
    if [ ! -f ./.env ]; then
        POSTGRES_PASSWORD=\$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 20)
        SECRET_KEY=\$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 128)
        export POSTGRES_PASSWORD SECRET_KEY
        envsubst < .env.tmpl > .env
    fi

    # Rename project directory
    if [ ! -d '$PROJECT' ]; then
        mv gobabygo '$PROJECT'
    fi

    # Replace all instances of gobabygo with new project name
    find ./ -type f -not -path '*/.git/*' -exec sed -i \"s/gobabygo/$PROJECT/gI\" {} +

    # Cleanup template files
    rm -f ./.env.tmpl ./bootstrap.sh ./LICENSE
"

# Build and start the application
docker compose build --build-arg uid=$(id -u) --build-arg gid=$(id -g)
docker compose run web bash -c \
    "python3 manage.py makemigrations && python3 manage.py migrate"
docker compose up $2

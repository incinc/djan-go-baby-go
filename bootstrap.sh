#!/usr/bin/env sh

set -eu

# Ensure Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required but not installed. Please install Docker first."
    exit 1
fi

PROJECT="${1:-}"

if [ -z "$PROJECT" ]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

# Validate project name is a valid Python identifier
if ! echo "$PROJECT" | grep -qE '^[a-z][a-z0-9_]*$'; then
    echo "$PROJECT is not a valid Python identifier. Use lowercase letters, digits and underscores, starting with a letter."
    exit 1
fi

# Reject Python keywords and names that collide with template directories/modules.
case "$PROJECT" in
    app|frontend|dev|static|templates|test|django|channels|mcp|celery|asgi|os|sys|keyword|abc|typing|json|asyncio|email|http|logging|collections|importlib|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)
        echo "$PROJECT is a reserved project name."
        exit 1
        ;;
esac
if [ "$PROJECT" != gobabygo ] && [ -e "$PROJECT" ]; then
    echo "$PROJECT already exists; choose a different project name."
    exit 1
fi

# Run the bootstrap process in a container
docker run --rm -v "$(pwd):/work" -w /work alpine:3.24 sh -ec "
    # Install required tools
    apk add --no-cache gettext

    # Validate project name
    if ! echo '$PROJECT' | grep -qE '^[a-z][a-z0-9_]*$'; then
        echo '$PROJECT is not a valid Python identifier. Use lowercase letters, digits and underscores, starting with a letter.'
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
    find ./ \( -name .git -o -name node_modules -o -name .venv -o -name __pycache__ -o -path ./static \) -prune -o -type f -exec sed -i \"s/gobabygo/$PROJECT/gI\" {} +

    # Cleanup template files
    rm -f ./.env.tmpl ./bootstrap.sh ./LICENSE
"

# Build and start the application
docker compose build --build-arg uid=$(id -u) --build-arg gid=$(id -g)
docker compose run --rm web bash -c \
    "python3 manage.py makemigrations && python3 manage.py migrate"
shift
docker compose up "$@"

#!/usr/bin/env bash

set -euo pipefail

# Python dependencies are managed with pip-tools. This simplifies adding a new dependency.
# To remove a dependency, remove it from requirements.in and run ./dev/requirements.sh recompile

if [[ "${1:-}" == "recompile"* ]]; then
    echo "Rebuilding from requirements.in..."
elif [[ "${1:-}" == "install"* ]]; then
    echo "Installing $2..."
    echo "$2" >> requirements.in
    sort -b requirements.in -o requirements.in
else
    echo "Invalid argument. Please use 'install' or 'recompile'."
    exit 1
fi

docker compose run --rm web bash -c "pip-compile --allow-unsafe --resolver=backtracking requirements.in"
docker compose build web

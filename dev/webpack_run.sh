#!/usr/bin/env bash

# The webpack container is built with node_modules in /opt/, one directory above /opt/src/ where the repo source code
# is mounted. This script simplifies running `npm` commands inside the webpack container, and copies the resulting
# package files up to the repo level so they can be source controlled.

echo "Running '$@' in webpack container..."
CMD="cd /opt/ && $@ && cp /opt/package*.json /opt/src/"
docker compose run webpack bash -c "$CMD"

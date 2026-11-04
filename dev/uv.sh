#!/usr/bin/env sh
set -eu

# Run uv against the source bind mount without needing uv/Python on the host.
# Use add/remove --no-sync to edit the manifests, then rebuild web and worker.
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <uv arguments> (e.g. add --no-sync httpx2)"
    exit 1
fi
exec docker compose run --rm --no-deps web uv "$@"

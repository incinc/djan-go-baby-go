#!/bin/sh
set -eu
: "${REDIS_PASSWORD:?Set REDIS_PASSWORD with fly secrets}"
# Re-enter the official entrypoint to drop privileges before starting Redis.
exec /usr/local/bin/docker-entrypoint.sh redis-server \
    --bind 0.0.0.0 :: --protected-mode yes \
    --dir /data --appendonly yes --appendfsync everysec \
    --requirepass "$REDIS_PASSWORD"

#!/bin/sh
set -eu
# Optionally use a direct database connection instead of a pooler for migrations.
if [ -n "${DATABASE_MIGRATION_URL:-}" ]; then
    export DATABASE_URL="$DATABASE_MIGRATION_URL"
fi
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput

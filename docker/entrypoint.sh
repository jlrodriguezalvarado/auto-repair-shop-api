#!/bin/sh
set -eu
if [ "${WAIT_FOR_DB:-true}" = "true" ]; then
  /app/docker/wait-for.sh "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}" "${DB_WAIT_TIMEOUT:-60}"
fi
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  python manage.py migrate --noinput
fi
if [ "${RUN_COLLECTSTATIC:-true}" = "true" ]; then
  python manage.py collectstatic --noinput --clear
fi
echo "Starting: $*"
exec "$@"

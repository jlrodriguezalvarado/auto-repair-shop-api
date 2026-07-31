#!/bin/sh
set -eu
. /app/docker/ensure-venv.sh
. /app/docker/wait-for-db.sh
if [ "$#" -gt 0 ]; then
  exec "$@"
fi
if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  python manage.py migrate --noinput
fi
if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
  python manage.py collectstatic --noinput
fi
exec gunicorn -b 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-2}" --timeout 60 config.wsgi:application

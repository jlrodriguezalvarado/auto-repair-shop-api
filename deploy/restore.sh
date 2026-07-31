#!/usr/bin/env bash
# Drop and recreate the production Postgres database, then load a backup.
# Supports plain SQL (.sql) and pg_dump custom format (.dump from backup.sh).
# Run on the server from /opt/apps/mechanics.
#
# Usage:
#   ./restore.sh /srv/backups/mechanics/mechanics-api-YYYYMMDD-HHMMSS.dump
#   ./restore.sh /path/to/dump.sql
#   ./restore.sh --yes /path/to/dump.sql   # skip confirmation
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f compose.production.yml --env-file .env --env-file .env.deploy)
YES=0
BACKUP_FILE=""

for arg in "$@"; do
  case "$arg" in
    --yes|-y) YES=1 ;;
    -h|--help)
      sed -n '2,10p' "$0"
      exit 0
      ;;
    -*)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
    *)
      BACKUP_FILE="$arg"
      ;;
  esac
done

if [[ -z "$BACKUP_FILE" ]]; then
  echo "Usage: $0 [--yes] /path/to/backup.sql|.dump" >&2
  exit 1
fi
if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Backup file not found: $BACKUP_FILE" >&2
  exit 1
fi
if [[ ! -f .env ]]; then
  echo "Missing .env (copy from .env.example and fill secrets)." >&2
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env
set +a
if [[ -f .env.deploy ]]; then
  # shellcheck disable=SC1091
  set -a
  source .env.deploy
  set +a
fi

: "${DB_USER:?DB_USER must be set in .env}"
: "${POSTGRES_DB:?POSTGRES_DB must be set in .env}"

case "$BACKUP_FILE" in
  *.sql|*.SQL) FORMAT=sql ;;
  *.dump|*.DUMP) FORMAT=custom ;;
  *)
    echo "Unsupported extension (use .sql or .dump): $BACKUP_FILE" >&2
    exit 1
    ;;
esac

echo "==> This will DESTROY database '${POSTGRES_DB}' and reload:"
echo "    file:   ${BACKUP_FILE}"
echo "    format: ${FORMAT}"
echo "    size:   $(du -h "$BACKUP_FILE" | awk '{print $1}')"
if [[ "$YES" -ne 1 ]]; then
  read -r -p "Type the database name to confirm: " confirm
  if [[ "$confirm" != "$POSTGRES_DB" ]]; then
    echo "Aborted." >&2
    exit 1
  fi
fi

echo "==> Ensuring db is up"
"${COMPOSE[@]}" up -d --wait db

echo "==> Stopping app services that hold DB connections"
"${COMPOSE[@]}" stop api worker beat 2>/dev/null || true

echo "==> Terminating open sessions on ${POSTGRES_DB}"
"${COMPOSE[@]}" exec -T db \
  psql -U "$DB_USER" -d postgres -v ON_ERROR_STOP=1 \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${POSTGRES_DB}' AND pid <> pg_backend_pid();"

echo "==> Dropping and recreating ${POSTGRES_DB}"
"${COMPOSE[@]}" exec -T db \
  psql -U "$DB_USER" -d postgres -v ON_ERROR_STOP=1 \
  -c "DROP DATABASE IF EXISTS \"${POSTGRES_DB}\";" \
  -c "CREATE DATABASE \"${POSTGRES_DB}\" OWNER \"${DB_USER}\";"

echo "==> Restoring backup"
if [[ "$FORMAT" == "sql" ]]; then
  "${COMPOSE[@]}" exec -T db \
    psql -U "$DB_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 \
    < "$BACKUP_FILE"
else
  "${COMPOSE[@]}" exec -T db \
    pg_restore -U "$DB_USER" -d "$POSTGRES_DB" --no-owner --role="$DB_USER" \
    < "$BACKUP_FILE"
fi

echo "==> Starting stack"
"${COMPOSE[@]}" up -d --remove-orphans

echo "Done. Database ${POSTGRES_DB} restored from ${BACKUP_FILE}."

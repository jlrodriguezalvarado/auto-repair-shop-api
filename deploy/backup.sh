#!/usr/bin/env bash
# Dump the production Postgres database (custom format). Run on the server.
# Reads secrets from .env next to this script.
#
# Retention (after each dump):
#   - last BACKUP_KEEP_DAILY calendar days (default 7: Mon–Sun rolling)
#   - last BACKUP_KEEP_MONTHLY month-end dumps (default 3; last day of each month)
#   - all other mechanics-api-*.dump files are deleted
#
# Usage (from /opt/apps/mechanics):
#   ./backup.sh
# Cron example (daily 00:00):
#   0 0 * * * cd /opt/apps/mechanics && ./backup.sh >> /var/log/mechanics-backup.log 2>&1
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f compose.production.yml --env-file .env --env-file .env.deploy)

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
BACKUP_DIR="${BACKUP_DIR:-${ROOT}/backups}"
BACKUP_KEEP_DAILY="${BACKUP_KEEP_DAILY:-7}"
BACKUP_KEEP_MONTHLY="${BACKUP_KEEP_MONTHLY:-3}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${BACKUP_DIR}/mechanics-api-${STAMP}.dump"

mkdir -p "$BACKUP_DIR"

echo "==> Dumping ${POSTGRES_DB} as ${DB_USER} → ${OUT}"
"${COMPOSE[@]}" exec -T db \
  pg_dump -U "$DB_USER" -d "$POSTGRES_DB" -Fc \
  > "$OUT"

echo "==> Wrote $(du -h "$OUT" | awk '{print $1}')"

# Newest dump for a calendar day YYYYMMDD (lexicographic stamp = newest time).
newest_for_day() {
  local day="$1"
  local best=""
  local f
  shopt -s nullglob
  for f in "${BACKUP_DIR}/mechanics-api-${day}-"*.dump; do
    if [[ -z "$best" || "$f" > "$best" ]]; then
      best="$f"
    fi
  done
  shopt -u nullglob
  printf '%s' "$best"
}

prune_backups() {
  local -A keep=()
  local i m day first last f today count
  today="$(date +%Y%m%d)"
  echo "==> Retention: ${BACKUP_KEEP_DAILY} daily + ${BACKUP_KEEP_MONTHLY} month-end in ${BACKUP_DIR}"
  for ((i = 0; i < BACKUP_KEEP_DAILY; i++)); do
    day="$(date -d "today - ${i} days" +%Y%m%d)"
    f="$(newest_for_day "$day")"
    if [[ -n "$f" ]]; then
      keep["$f"]=1
    fi
  done
  count=0
  for ((m = 0; count < BACKUP_KEEP_MONTHLY; m++)); do
    first="$(date -d "$(date +%Y-%m-01) - ${m} month" +%Y-%m-%d)"
    last="$(date -d "${first} +1 month -1 day" +%Y%m%d)"
    if [[ "$last" -gt "$today" ]]; then
      continue
    fi
    f="$(newest_for_day "$last")"
    if [[ -n "$f" ]]; then
      keep["$f"]=1
    fi
    count=$((count + 1))
  done
  shopt -s nullglob
  for f in "${BACKUP_DIR}"/mechanics-api-*.dump; do
    if [[ -z "${keep[$f]:-}" ]]; then
      echo "    prune $(basename "$f")"
      rm -f "$f"
    else
      echo "    keep  $(basename "$f")"
    fi
  done
  shopt -u nullglob
}

prune_backups

echo "Done."

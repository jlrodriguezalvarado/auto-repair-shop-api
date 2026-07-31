#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f compose.production.yml --env-file .env --env-file .env.deploy)

if [[ ! -f .env ]]; then
  echo "Missing .env (copy from .env.example and fill secrets)." >&2
  exit 1
fi
if [[ ! -f .env.deploy ]]; then
  echo "Missing .env.deploy with APP_VERSION and WEB_VERSION." >&2
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env.deploy
set +a

if [[ -z "${APP_VERSION:-}" || -z "${WEB_VERSION:-}" ]]; then
  echo "APP_VERSION and WEB_VERSION must be set in .env.deploy." >&2
  exit 1
fi

echo "==> Pulling mechanics/api:${APP_VERSION} and mechanics/web:${WEB_VERSION}"
"${COMPOSE[@]}" pull

echo "==> Starting database (required before migrate)"
"${COMPOSE[@]}" up -d --wait db

echo "==> Migrating database"
"${COMPOSE[@]}" run --rm --no-deps --entrypoint python api \
  manage.py migrate --noinput

echo "==> Starting stack"
"${COMPOSE[@]}" up -d --remove-orphans

echo "==> Waiting for API readiness inside the container"
READY_PROBE='import urllib.request; urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8000/health/ready/", headers={"X-Forwarded-Proto": "https"}), timeout=3)'
for _ in $(seq 1 30); do
  if "${COMPOSE[@]}" exec -T api \
    python -c "${READY_PROBE}" \
    >/dev/null 2>&1; then
    echo "API ready."
    "${COMPOSE[@]}" ps
    exit 0
  fi
  sleep 2
done

echo "API did not become ready in time. Check logs:" >&2
"${COMPOSE[@]}" logs --tail=80 api
exit 1

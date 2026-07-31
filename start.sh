#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"
COMPOSE=(docker compose -f "${COMPOSE_FILE:-docker-compose.yml}")
APP_PORT="${APP_PORT:-8001}"
export RUN_MIGRATIONS="${RUN_MIGRATIONS:-1}"
export RUN_COLLECTSTATIC="${RUN_COLLECTSTATIC:-1}"
POSTGRES_DB_NAME="${POSTGRES_DB_NAME:-mechanics_api}"
for arg in "$@"; do
  case "$arg" in
    -h|--help)
      echo "Usage: ./start.sh"
      echo "  Requires shared docker-tools (Postgres) on network dev-tools."
      echo "  Ensures DB, then starts the API container."
      exit 0
      ;;
  esac
done

port_in_use() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn "sport = :${port}" 2>/dev/null | grep -q LISTEN
    return $?
  fi
  if command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
    return $?
  fi
  return 1
}

owned_by_compose() {
  local port="$1"
  local cname="$2"
  docker ps --format '{{.Names}} {{.Ports}}' 2>/dev/null \
    | grep -E "^${cname} " \
    | grep -q ":${port}->"
}

check_port() {
  local port="$1"
  local cname="$2"
  local label="$3"
  if ! port_in_use "$port"; then
    return 0
  fi
  if owned_by_compose "$port" "$cname"; then
    echo "[start] Port ${port} already used by ${cname} (ok)."
    return 0
  fi
  echo "[start] ERROR: Port ${port} (${label}) is already allocated by another process." >&2
  echo "[start] Free it or change the port in .env, then retry. Aborting." >&2
  exit 1
}

env_get() {
  local key="$1"
  local file=".env"
  [ -f "$file" ] || return 0
  local line
  line="$(grep -E "^[[:space:]]*${key}=" "$file" | tail -n1 || true)"
  [ -n "$line" ] || return 0
  local val="${line#*=}"
  val="${val%$'\r'}"
  val="${val#\"}"
  val="${val%\"}"
  val="${val#\'}"
  val="${val%\'}"
  printf '%s' "$val"
}

resolve_docker_tools_dir() {
  local from_env=""
  from_env="$(env_get DOCKER_TOOLS_DIR)"
  if [ -n "${DOCKER_TOOLS_DIR:-}" ]; then
    printf '%s' "$DOCKER_TOOLS_DIR"
    return 0
  fi
  if [ -n "$from_env" ]; then
    printf '%s' "$from_env"
    return 0
  fi
  local candidates=(
    "${ROOT_DIR}/../../docker-tools"
    "/home/jlrodriguez/projects/docker-tools"
  )
  local c
  for c in "${candidates[@]}"; do
    if [ -d "$c" ] && [ -x "$c/scripts/ensure-db.sh" ]; then
      (cd "$c" && pwd)
      return 0
    fi
  done
  return 1
}

if ! docker info >/dev/null 2>&1; then
  echo "[start] ERROR: Docker daemon is not reachable. Start Docker inside WSL2 first." >&2
  exit 1
fi

if [ -f .env ]; then
  _app="$(env_get APP_PORT)"
  _db="$(env_get POSTGRES_DB)"
  [ -n "${_app}" ] && APP_PORT="${_app}"
  [ -n "${_db}" ] && POSTGRES_DB_NAME="${_db}"
fi
APP_PORT="${APP_PORT:-8001}"
POSTGRES_DB_NAME="${POSTGRES_DB_NAME:-mechanics_api}"

check_port "$APP_PORT" "mechanics_api_app" "API"

if ! DOCKER_TOOLS_DIR="$(resolve_docker_tools_dir)"; then
  echo "[start] ERROR: docker-tools not found." >&2
  echo "[start] Clone/create it at /home/jlrodriguez/projects/docker-tools or set DOCKER_TOOLS_DIR." >&2
  exit 1
fi
echo "[start] Using docker-tools at ${DOCKER_TOOLS_DIR}"

if ! docker network inspect dev-tools >/dev/null 2>&1; then
  echo "[start] ERROR: Docker network 'dev-tools' is missing." >&2
  echo "[start] Start shared tools first: cd ${DOCKER_TOOLS_DIR} && ./start.sh" >&2
  exit 1
fi

pg_health="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}unknown{{end}}' tools_postgres 2>/dev/null || echo missing)"
if [ "$pg_health" != "healthy" ]; then
  echo "[start] ERROR: docker-tools postgres is not healthy (postgres=${pg_health})." >&2
  echo "[start] Start shared tools first: cd ${DOCKER_TOOLS_DIR} && ./start.sh" >&2
  exit 1
fi

echo "[start] Ensuring Postgres database '${POSTGRES_DB_NAME}'..."
"${DOCKER_TOOLS_DIR}/scripts/ensure-db.sh" "$POSTGRES_DB_NAME"

echo "[start] Validating Compose config..."
"${COMPOSE[@]}" config --quiet
echo "[start] Starting app services..."
"${COMPOSE[@]}" up -d --remove-orphans --pull missing
echo "[start] Stack is up."
"${COMPOSE[@]}" ps
echo "[start] API: http://localhost:${APP_PORT}"
echo "[start] Shared pgAdmin: http://localhost:5050 (docker-tools)"
echo "[start] Logs: docker compose logs -f mechanics_api_app"
docker exec -it mechanics_api_app bash

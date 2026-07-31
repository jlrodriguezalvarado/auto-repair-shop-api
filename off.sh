#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"
COMPOSE=(docker compose -f "${COMPOSE_FILE:-docker-compose.yml}")
STOP_TIMEOUT="${STOP_TIMEOUT:-${COMPOSE_STOP_TIMEOUT:-45}}"
FORCE=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    -h|--help)
      echo "Usage: ./off.sh [--force]"
      echo "  Graceful stop with ${STOP_TIMEOUT}s timeout (override via STOP_TIMEOUT)."
      echo "  --force  Kill remaining project containers after graceful down."
      exit 0
      ;;
  esac
done

if ! docker info >/dev/null 2>&1; then
  echo "[off] ERROR: Docker daemon is not reachable." >&2
  exit 1
fi

echo "[off] Stopping services (timeout ${STOP_TIMEOUT}s)..."
"${COMPOSE[@]}" stop --timeout "$STOP_TIMEOUT" 2>/dev/null || true
echo "[off] Removing containers and orphaned resources..."
"${COMPOSE[@]}" down --remove-orphans --timeout "$STOP_TIMEOUT"

if [ "$FORCE" -eq 1 ]; then
  echo "[off] Force-removing any leftover mechanics_api containers..."
  for name in mechanics_api_app; do
    if docker ps -aq -f "name=^${name}$" | grep -q .; then
      docker rm -f "$name" >/dev/null 2>&1 || true
    fi
  done
fi

echo "[off] Done."

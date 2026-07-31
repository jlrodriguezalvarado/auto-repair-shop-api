#!/bin/sh
# Wait for PostgreSQL then exit 1 if unreachable (no infinite retry — safer on WSL2).
set -eu
DB_HOST="${DB_HOST:-tools_postgres}"
DB_PORT_INTERNAL="${DB_PORT_INTERNAL:-5432}"
MAX_WAIT="${DB_WAIT_SECONDS:-60}"
echo "[entrypoint] Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT_INTERNAL}..."
elapsed=0
until python - <<PY
import os, socket, sys
host = os.environ.get("DB_HOST", "tools_postgres")
port = int(os.environ.get("DB_PORT_INTERNAL", "5432"))
try:
    with socket.create_connection((host, port), timeout=2):
        sys.exit(0)
except OSError:
    sys.exit(1)
PY
do
  elapsed=$((elapsed + 2))
  if [ "$elapsed" -ge "$MAX_WAIT" ]; then
    echo "[entrypoint] ERROR: PostgreSQL not reachable after ${MAX_WAIT}s. Exiting without retry loop." >&2
    exit 1
  fi
  sleep 2
done
echo "[entrypoint] PostgreSQL is reachable."

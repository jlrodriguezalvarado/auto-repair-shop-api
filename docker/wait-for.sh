#!/bin/sh
set -eu
host="${1:-localhost}"
port="${2:-5432}"
timeout="${3:-60}"
interval=1
elapsed=0
echo "Waiting for ${host}:${port} (timeout ${timeout}s)..."
while ! nc -z "$host" "$port" >/dev/null 2>&1; do
  if [ "$elapsed" -ge "$timeout" ]; then
    echo "Timed out waiting for ${host}:${port}" >&2
    exit 1
  fi
  sleep "$interval"
  elapsed=$((elapsed + interval))
done
echo "${host}:${port} is available."

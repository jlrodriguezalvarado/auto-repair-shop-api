#!/bin/sh
set -eu
project="${COMPOSE_PROJECT_NAME:-auto-repair-shop-api}"
echo "Stopping stack for project '${project}'..."
docker compose --project-name "$project" down --remove-orphans --timeout 30 "$@"
echo "Stack stopped."

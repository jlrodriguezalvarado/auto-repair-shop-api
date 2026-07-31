#!/usr/bin/env bash
# Build the production API image and optionally push.
# Syncs APP_VERSION into deploy/.env.deploy (from .env.docker or git SHA).
# Usage (from auto-repair-shop-api/):
#   cp --update=none .env.docker.example .env.docker   # once (optional)
#   ./deploy/build-image.sh                # build
#   ./deploy/build-image.sh --push         # build + push
set -Eeuo pipefail

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${DEPLOY_DIR}/.." && pwd)"
cd "$ROOT"
ENV_DEPLOY="${DEPLOY_DIR}/.env.deploy"
ENV_DEPLOY_EXAMPLE="${DEPLOY_DIR}/.env.deploy.example"

upsert_env() {
  local file="$1" key="$2" value="$3"
  if [[ -f "$file" ]] && grep -q "^${key}=" "$file"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$file"
  else
    printf '%s=%s\n' "$key" "$value" >> "$file"
  fi
}

ENV_FILE="${ROOT}/.env.docker"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  set +a
fi

REGISTRY_HOST="${REGISTRY_HOST:-registry.lumuscore.com}"
API_IMAGE="${API_IMAGE:-mechanics/api}"
APP_VERSION="${APP_VERSION:-$(git rev-parse --short HEAD)}"
PUSH=0

for arg in "$@"; do
  case "$arg" in
    --push) PUSH=1 ;;
    -h|--help)
      sed -n '2,8p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg (use --push)" >&2
      exit 1
      ;;
  esac
done

IMAGE="${REGISTRY_HOST}/${API_IMAGE}:${APP_VERSION}"

echo "==> Building ${IMAGE}"
docker build --pull \
  -t "${IMAGE}" \
  .

if [[ "$PUSH" -eq 1 ]]; then
  echo "==> Pushing ${IMAGE}"
  docker push "${IMAGE}"
fi

echo "==> Syncing APP_VERSION=${APP_VERSION} → ${ENV_DEPLOY}"
if [[ ! -f "$ENV_DEPLOY" ]]; then
  if [[ ! -f "$ENV_DEPLOY_EXAMPLE" ]]; then
    echo "Missing ${ENV_DEPLOY_EXAMPLE}" >&2
    exit 1
  fi
  cp "$ENV_DEPLOY_EXAMPLE" "$ENV_DEPLOY"
fi
upsert_env "$ENV_DEPLOY" APP_VERSION "$APP_VERSION"

echo "APP_VERSION=${APP_VERSION}"
echo "IMAGE=${IMAGE}"
echo "ENV_DEPLOY=${ENV_DEPLOY}"

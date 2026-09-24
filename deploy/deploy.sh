#!/usr/bin/env bash
# Rolling deploy: keep the old container in Traefik until the new one is ready.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
COMPOSE=(docker compose -f compose.production.yml --env-file .env --env-file .env.deploy)
PROXY_NET="${PROXY_NETWORK:-proxy}"
DRAIN_SECONDS="${DRAIN_SECONDS:-4}"
READY_ATTEMPTS="${READY_ATTEMPTS:-45}"
STOP_TIMEOUT="${STOP_TIMEOUT:-25}"
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
source .env
source .env.deploy
set +a
PROXY_NET="${PROXY_NETWORK:-proxy}"
if [[ -z "${APP_VERSION:-}" || -z "${WEB_VERSION:-}" ]]; then
  echo "APP_VERSION and WEB_VERSION must be set in .env.deploy." >&2
  exit 1
fi
if [[ -z "${REGISTRY_HOST:-}" ]]; then
  echo "REGISTRY_HOST must be set in .env." >&2
  exit 1
fi
DJANGO_READY_PROBE='import urllib.request; urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8000/health/ready/", headers={"X-Forwarded-Proto": "https"}), timeout=3)'
running_ids() {
  local service="$1"
  "${COMPOSE[@]}" ps -q --status running "$service" 2>/dev/null || true
}
probe_ready() {
  local cid="$1" kind="$2"
  if [[ "$kind" == "django" ]]; then
    docker exec -T "$cid" python -c "${DJANGO_READY_PROBE}" >/dev/null 2>&1
  else
    docker exec -T "$cid" wget -qO- http://127.0.0.1/ >/dev/null 2>&1
  fi
}
wait_ready() {
  local cid="$1" kind="$2"
  local i
  for i in $(seq 1 "${READY_ATTEMPTS}"); do
    if probe_ready "$cid" "$kind"; then
      return 0
    fi
    sleep 2
  done
  return 1
}
detach_proxy() {
  local cid="$1"
  docker network disconnect "${PROXY_NET}" "$cid" >/dev/null 2>&1 || true
}
attach_proxy() {
  local cid="$1"
  if docker inspect --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' "$cid" | grep -qw "${PROXY_NET}"; then
    return 0
  fi
  docker network connect "${PROXY_NET}" "$cid"
}
ids_match() {
  local needle="$1"
  shift
  local id
  for id in "$@"; do
    if [[ "$id" == "$needle" ]]; then
      return 0
    fi
  done
  return 1
}
start_fresh() {
  local service="$1" kind="$2"
  echo "==> ${service}: no running replica, starting one"
  "${COMPOSE[@]}" up -d --no-deps --scale "${service}=1" "$service"
  local cid attempt
  cid=""
  for attempt in $(seq 1 10); do
    cid="$(running_ids "$service" | awk 'NF' | head -n1 || true)"
    if [[ -n "$cid" ]]; then
      break
    fi
    sleep 1
  done
  if [[ -z "$cid" ]]; then
    echo "${service}: container did not start." >&2
    "${COMPOSE[@]}" logs --tail=80 "$service"
    return 1
  fi
  if ! wait_ready "$cid" "$kind"; then
    echo "${service}: did not become ready in time." >&2
    "${COMPOSE[@]}" logs --tail=80 "$service"
    return 1
  fi
  echo "==> ${service}: ready"
}
rolling_replace() {
  local service="$1" image="$2" kind="$3"
  local use_proxy="${4:-1}"
  local old_raw new_raw
  local -a old_ids=() new_ids=() now_ids=()
  local old_id new_id drop_id attempt
  old_raw="$(running_ids "$service")"
  if [[ -z "${old_raw//[$' \t\n']/}" ]]; then
    start_fresh "$service" "$kind"
    return
  fi
  while IFS= read -r old_id; do
    [[ -n "$old_id" ]] && old_ids+=("$old_id")
  done <<<"$old_raw"
  echo "==> ${service}: rolling ${#old_ids[@]} replica(s) → ${image}"
  "${COMPOSE[@]}" up -d --no-deps --no-recreate --scale "${service}=$((${#old_ids[@]} + 1))" "$service"
  for attempt in $(seq 1 20); do
    new_ids=()
    new_raw="$(running_ids "$service")"
    while IFS= read -r new_id; do
      [[ -z "$new_id" ]] && continue
      if ids_match "$new_id" "${old_ids[@]}"; then
        continue
      fi
      new_ids+=("$new_id")
    done <<<"$new_raw"
    if [[ ${#new_ids[@]} -gt 0 ]]; then
      break
    fi
    sleep 1
  done
  if [[ ${#new_ids[@]} -eq 0 ]]; then
    echo "${service}: compose did not start a new replica (check --no-recreate/--scale support)." >&2
    return 1
  fi
  if [[ "$use_proxy" == "1" ]]; then
    for new_id in "${new_ids[@]}"; do
      detach_proxy "$new_id"
    done
  fi
  for new_id in "${new_ids[@]}"; do
    if ! wait_ready "$new_id" "$kind"; then
      echo "${service}: new replica ${new_id:0:12} failed readiness; leaving the previous replica up." >&2
      "${COMPOSE[@]}" logs --tail=80 "$service"
      for drop_id in "${new_ids[@]}"; do
        docker stop -t 5 "$drop_id" >/dev/null 2>&1 || true
        docker rm -f "$drop_id" >/dev/null 2>&1 || true
      done
      "${COMPOSE[@]}" up -d --no-deps --no-recreate --scale "${service}=${#old_ids[@]}" "$service" >/dev/null
      return 1
    fi
  done
  if [[ "$use_proxy" == "1" ]]; then
    for new_id in "${new_ids[@]}"; do
      attach_proxy "$new_id"
    done
    echo "==> ${service}: new replica ready, draining old replica from Traefik"
    sleep "${DRAIN_SECONDS}"
    for old_id in "${old_ids[@]}"; do
      if docker inspect "$old_id" >/dev/null 2>&1; then
        detach_proxy "$old_id"
      else
        echo "==> ${service}: previous replica ${old_id:0:12} already gone (compose recreated; a short gap is possible)"
      fi
    done
    sleep "${DRAIN_SECONDS}"
  else
    echo "==> ${service}: new replica ready, stopping old replica"
  fi
  for old_id in "${old_ids[@]}"; do
    docker stop -t "${STOP_TIMEOUT}" "$old_id" >/dev/null 2>&1 || true
    docker rm -f "$old_id" >/dev/null 2>&1 || true
  done
  "${COMPOSE[@]}" up -d --no-deps --no-recreate --scale "${service}=1" "$service" >/dev/null
  now_ids=()
  new_raw="$(running_ids "$service")"
  while IFS= read -r new_id; do
    [[ -n "$new_id" ]] && now_ids+=("$new_id")
  done <<<"$new_raw"
  if [[ ${#now_ids[@]} -ne 1 ]]; then
    echo "${service}: expected 1 running replica after drain, found ${#now_ids[@]}." >&2
    return 1
  fi
  echo "==> ${service}: rolled to ${now_ids[0]:0:12}"
}
echo "==> Pulling mechanics/api:${APP_VERSION} and mechanics/web:${WEB_VERSION}"
"${COMPOSE[@]}" pull
echo "==> Starting database (required before migrate)"
"${COMPOSE[@]}" up -d --wait db
echo "==> Migrating database"
"${COMPOSE[@]}" run --rm --no-deps --entrypoint python \
  --label traefik.enable=false \
  api manage.py migrate --noinput
echo "==> Rolling stack (old replica stays in Traefik until the new one is ready)"
rolling_replace api "${REGISTRY_HOST}/mechanics/api:${APP_VERSION}" django 1
rolling_replace web "${REGISTRY_HOST}/mechanics/web:${WEB_VERSION}" static 1
echo "==> Stack ready"
"${COMPOSE[@]}" ps

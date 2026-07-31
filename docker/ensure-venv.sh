#!/bin/sh
# Recreate /app/venv when missing (bind mount does not include host venv by default).
set -eu
VENV_DIR="${VIRTUAL_ENV:-/app/venv}"
REQ_FILE="${REQUIREMENTS_FILE:-local.txt}"
REQ_PATH="/app/requirements/${REQ_FILE}"
if [ ! -x "${VENV_DIR}/bin/python" ]; then
  echo "[ensure-venv] Creating ${VENV_DIR} from ${REQ_PATH}..."
  # System interpreter from the image (venv bin is missing under the bind mount).
  /usr/local/bin/python -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/pip" install --no-cache-dir --upgrade pip
  "${VENV_DIR}/bin/pip" install --no-cache-dir -r "${REQ_PATH}"
  echo "[ensure-venv] Ready."
fi
export VIRTUAL_ENV="${VENV_DIR}"
export PATH="${VENV_DIR}/bin:${PATH}"

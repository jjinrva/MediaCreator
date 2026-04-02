#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_PYTHON="$ROOT_DIR/apps/api/.venv/bin/python"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if [[ ! -x "$API_PYTHON" ]]; then
  echo "MediaCreator API environment is missing. Run 'make bootstrap-api' or 'make bootstrap' first." >&2
  exit 1
fi

export PYTHONPATH="$ROOT_DIR/apps/api:$ROOT_DIR/apps/worker/src${PYTHONPATH:+:$PYTHONPATH}"

exec "$API_PYTHON" -m mediacreator_worker.main

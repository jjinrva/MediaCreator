#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKER_BIN="$ROOT_DIR/apps/worker/.venv/bin/mediacreator-worker"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if [[ ! -x "$WORKER_BIN" ]]; then
  echo "MediaCreator worker environment is missing. Run 'make bootstrap-worker' or 'make bootstrap' first." >&2
  exit 1
fi

export PYTHONPATH="$ROOT_DIR/apps/api:$ROOT_DIR/apps/worker/src${PYTHONPATH:+:$PYTHONPATH}"

exec "$WORKER_BIN"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_BIN="$ROOT_DIR/apps/api/.venv/bin/uvicorn"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if [[ ! -x "$API_BIN" ]]; then
  echo "MediaCreator API environment is missing. Run 'make bootstrap-api' or 'make bootstrap' first." >&2
  exit 1
fi

cd "$ROOT_DIR/apps/api"
exec "$API_BIN" app.main:app --reload --host "${MEDIACREATOR_API_HOST:-0.0.0.0}" --port "${MEDIACREATOR_API_PORT:-8010}"

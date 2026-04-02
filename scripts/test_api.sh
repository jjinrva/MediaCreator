#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTEST_BIN="$ROOT_DIR/apps/api/.venv/bin/pytest"

if [[ ! -x "$PYTEST_BIN" ]]; then
  echo "MediaCreator API environment is missing. Run 'make bootstrap-api' or 'make install' first." >&2
  exit 1
fi

cd "$ROOT_DIR/apps/api"
exec "$PYTEST_BIN" tests

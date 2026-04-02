#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PNPM_BIN="$ROOT_DIR/infra/bin/pnpm"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if [[ ! -x "$PNPM_BIN" ]]; then
  echo "MediaCreator pnpm runtime is missing. Run 'make bootstrap' first." >&2
  exit 1
fi

cd "$ROOT_DIR/apps/web"
exec env PATH="$ROOT_DIR/infra/bin:$PATH" "$PNPM_BIN" dev --hostname "${MEDIACREATOR_WEB_HOST:-0.0.0.0}" --port "${MEDIACREATOR_WEB_PORT:-3000}"

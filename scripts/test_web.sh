#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PNPM_BIN="$ROOT_DIR/infra/bin/pnpm"
PLAYWRIGHT_BROWSERS_PATH="$ROOT_DIR/infra/playwright"

if [[ ! -x "$PNPM_BIN" ]]; then
  echo "MediaCreator pnpm runtime is missing. Run 'make install' first." >&2
  exit 1
fi

PATH="$ROOT_DIR/infra/bin:$PATH" "$PNPM_BIN" --dir "$ROOT_DIR/apps/web" test
PATH="$ROOT_DIR/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_BROWSERS_PATH" "$PNPM_BIN" --dir "$ROOT_DIR/apps/web" exec playwright install chromium
exec env PATH="$ROOT_DIR/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_BROWSERS_PATH" "$PNPM_BIN" --dir "$ROOT_DIR/apps/web" test:e2e

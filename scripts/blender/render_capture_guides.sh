#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BLENDER_BIN="${MEDIACREATOR_BLENDER_BIN:-/opt/blender-4.5-lts/blender}"
OUTPUT_DIR="${1:-$ROOT_DIR/docs/capture_guides/assets}"
SCRIPT_PATH="$ROOT_DIR/scripts/blender/render_capture_guides.py"

if [[ ! -x "$BLENDER_BIN" ]]; then
  echo "Blender 4.5 LTS is missing at '$BLENDER_BIN'." >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
exec "$BLENDER_BIN" --background --factory-startup --python "$SCRIPT_PATH" -- "$OUTPUT_DIR"

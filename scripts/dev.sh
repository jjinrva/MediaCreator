#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/infra/docker-compose.yml"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for Phase 02 local runtime. Install Docker first." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose is required for Phase 02 local runtime." >&2
  exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Missing Compose file at $COMPOSE_FILE." >&2
  exit 1
fi

cleanup() {
  jobs -p | xargs -r kill
}

trap cleanup EXIT INT TERM

echo "Starting PostgreSQL with Docker Compose..."
docker compose -f "$COMPOSE_FILE" up -d postgres >/dev/null

for _ in $(seq 1 30); do
  if docker compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U "${MEDIACREATOR_DB_USER:-mediacreator}" -d "${MEDIACREATOR_DB_NAME:-mediacreator}" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! docker compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U "${MEDIACREATOR_DB_USER:-mediacreator}" -d "${MEDIACREATOR_DB_NAME:-mediacreator}" >/dev/null 2>&1; then
  echo "PostgreSQL did not become ready in time." >&2
  exit 1
fi

echo "Starting API, web, and worker..."

(
  exec "$ROOT_DIR/scripts/run-api.sh"
) &

(
  exec "$ROOT_DIR/scripts/run-web.sh"
) &

(
  exec "$ROOT_DIR/scripts/run_worker.sh"
) &

wait

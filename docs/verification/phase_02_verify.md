# Phase 02 verification

## Scope verified

- PostgreSQL 16 Docker Compose startup and readiness
- API startup from source and `/health` success response
- Web startup from source and truthful landing-page rendering
- Worker startup, idle logging, and clean shutdown
- `make dev` launching PostgreSQL, API, web, and worker together
- Environment contract presence in `.env.example`, `README.md`, and `docs/architecture/local_runtime.md`
- Absence of Redis, Celery, or other extra runtime services in this phase
- Required targeted tests plus lint/typecheck regression gates

## Commands run

- `docker compose -f /opt/MediaCreator/infra/docker-compose.yml up -d postgres`
- `for i in $(seq 1 30); do if docker compose -f /opt/MediaCreator/infra/docker-compose.yml exec -T postgres pg_isready -U mediacreator -d mediacreator >/dev/null 2>&1; then exit 0; fi; sleep 1; done; exit 1`
- `docker compose -f /opt/MediaCreator/infra/docker-compose.yml ps`
- `make api`
- `curl -fsS http://127.0.0.1:8010/health`
- `make web`
- `curl -fsS http://127.0.0.1:3000 | rg -n "MediaCreator|single-user mode|Phase 02 local runtime"`
- `make worker`
- `make dev`
- `curl -fsS http://127.0.0.1:8010/health`
- `curl -fsS http://127.0.0.1:3000 | rg -n "MediaCreator|single-user mode|Phase 02 local runtime"`
- `rg -n "MEDIACREATOR_DB_PORT|MEDIACREATOR_DB_NAME|MEDIACREATOR_DB_USER|MEDIACREATOR_DB_PASSWORD|MEDIACREATOR_DATABASE_URL|MEDIACREATOR_STORAGE_SCRATCH_ROOT|MEDIACREATOR_STORAGE_NAS_ROOT|MEDIACREATOR_COMFYUI_ROOT|MEDIACREATOR_BLENDER_BIN|MEDIACREATOR_WORKER_CONCURRENCY|make bootstrap|make dev|docker compose -f infra/docker-compose.yml up -d postgres" /opt/MediaCreator/.env.example /opt/MediaCreator/README.md /opt/MediaCreator/docs/architecture/local_runtime.md`
- `docker compose -f /opt/MediaCreator/infra/docker-compose.yml config --services`
- `rg -n -i "redis|celery" /opt/MediaCreator/infra/docker-compose.yml /opt/MediaCreator/scripts /opt/MediaCreator/Makefile /opt/MediaCreator/README.md /opt/MediaCreator/docs/architecture/local_runtime.md`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Files changed in the phase

- `infra/docker-compose.yml`
- `scripts/dev.sh`
- `scripts/run-api.sh`
- `scripts/run-web.sh`
- `scripts/run-worker.sh`
- `.env.example`
- `Makefile`
- `README.md`
- `docs/architecture/local_runtime.md`
- `docs/phase_reports/phase_02.md`
- `docs/verification/phase_02_verify.md`
- `apps/api/app/schemas/health.py`
- `apps/api/app/services/health_service.py`
- `apps/api/tests/test_health.py`
- `apps/web/app/layout.tsx`
- `apps/web/app/page.tsx`
- `apps/web/tests/unit/home.test.tsx`
- `apps/web/tests/e2e/home.spec.ts`
- `apps/worker/src/mediacreator_worker/main.py`

## Results

- PASS: `docker compose -f /opt/MediaCreator/infra/docker-compose.yml up -d postgres` started only the `postgres` service, and `docker compose ... ps` reported it healthy on `127.0.0.1:54329`.
- PASS: `make api` served `/health`, and `curl -fsS http://127.0.0.1:8010/health` returned `{"application":"MediaCreator","service":"api","status":"ok","mode":"single-user","phase":"02"}`.
- PASS: `make web` rendered the landing page, and the page content included `MediaCreator`, `Phase 02 local runtime`, and `single-user mode`.
- PASS: `make worker` started the worker, logged bootstrap status, and shut down cleanly after interruption.
- PASS: `make dev` started PostgreSQL, API, web, and worker together, and both the API and landing page were reachable while it ran.
- PASS: `.env.example`, `README.md`, and `docs/architecture/local_runtime.md` all document the Phase 02 environment contract and startup commands.
- PASS: `docker compose ... config --services` returned only `postgres`, and there were no Redis or Celery references in the Phase 02 runtime surface beyond the explicit policy statement that they are absent.
- PASS: `make test-api`, `make test-web`, `make lint`, and `make typecheck` all completed successfully.

## PASS/FAIL decision

PASS

## Remaining risks

- Playwright still emits `NO_COLOR` warnings in this environment, but the smoke spec passes.
- Stopping `make api`, `make web`, `make worker`, and `make dev` with `Ctrl+C` returns a non-zero shell status even though the processes shut down cleanly; this is expected for interrupted foreground processes.
- The database container is live, but no schema exists yet by design.

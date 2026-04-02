# Phase 05 report

## Status

PASS

## What changed

- Added a durable PostgreSQL-backed job foundation with canonical states, progress fields, step names, error summaries, timestamps, and output references.
- Added a single service layer for enqueue, claim, progress, complete, fail, and cancel transitions, and made each transition write a linked `history_events` row.
- Added a minimal `GET /api/v1/jobs/{public_id}` route and response schema for truthful job-state reads.
- Added Alembic migration `0002_jobs_and_history_foundation` so the new job columns and `history_events.job_id` evolve from the Phase 04 baseline instead of changing the original migration.
- Replaced the worker bootstrap-only loop with a real PostgreSQL polling loop that uses `FOR UPDATE SKIP LOCKED` semantics through the shared job service.
- Added focused temp-database test helpers plus queue-domain tests covering single-claim behavior, `SKIP LOCKED`, API state reads, and history trails.
- Updated the landing page, worker README, runtime docs, and root README so the UI and docs no longer claim that the worker is idle-only.
- Fixed follow-up verification issues before final PASS:
  - added explicit typing for `JOB_PAYLOAD_ADAPTER`
  - corrected the FastAPI yield override used by the job-route tests
  - added worker `mypy_path` configuration so worker type-checks can resolve the shared API package
  - normalized import ordering with Ruff in the new API and worker files

## Exact commands run

- `docker compose -f infra/docker-compose.yml up -d postgres`
- `make bootstrap-api`
- `make bootstrap-worker`
- `apps/api/.venv/bin/pytest apps/api/tests/test_jobs_service.py apps/api/tests/test_db_migrations.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/home.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright install chromium`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/home.spec.ts`
- `apps/api/.venv/bin/alembic -c apps/api/alembic.ini upgrade head`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`
- `cd /opt/MediaCreator/apps/api && .venv/bin/ruff check app tests --fix`
- `cd /opt/MediaCreator/apps/worker && .venv/bin/ruff check src --fix`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Tests that passed

- `apps/api/.venv/bin/pytest apps/api/tests/test_jobs_service.py apps/api/tests/test_db_migrations.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/home.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/home.spec.ts`
- `apps/api/.venv/bin/alembic -c apps/api/alembic.ini upgrade head`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Remaining risks

- The worker loop is single-process and intentionally limited to the `noop` and `failing-noop` job kinds until later phases add real media pipelines.
- There is no mutation API for enqueue, cancel, or retry yet; Phase 05 only establishes the internal service and read route foundation.
- Output asset/storage references are wired into the schema now, but this phase does not yet create real derived assets or files.

## Next phase may start

Yes. Phase 05 verification passed, so Phase 06 may start.

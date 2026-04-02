# Local runtime

## Runtime model

Phase 02 uses a mixed local runtime:

- PostgreSQL 16 runs in Docker Compose
- the FastAPI app runs from source in `apps/api`
- the Next.js app runs from source in `apps/web`
- the worker runs from source in `apps/worker`
- ComfyUI runs as a separate local service when generation capability is being checked

No Redis, Celery, or other runtime services are part of this phase.

## Compose service

- Compose file: `infra/docker-compose.yml`
- Required service: `postgres`
- Default host port: `54329`
- Default database name: `mediacreator`
- Default database user: `mediacreator`
- Default database password: `mediacreator`

## Canonical commands

- `make bootstrap` — install the local Node 22 toolchain, resolve the pnpm workspace, and bootstrap the Python environments
- `make dev` — start PostgreSQL if needed, wait for readiness, then run API, web, and worker from source
- `make api` — run only the API
- `make web` — run only the web app
- `make worker` — run only the worker

## Environment variables

The runtime contract starts in `.env.example`:

- `MEDIACREATOR_DB_HOST`
- `MEDIACREATOR_DB_PORT`
- `MEDIACREATOR_DB_NAME`
- `MEDIACREATOR_DB_USER`
- `MEDIACREATOR_DB_PASSWORD`
- `MEDIACREATOR_DATABASE_URL`
- `MEDIACREATOR_STORAGE_SCRATCH_ROOT`
- `MEDIACREATOR_STORAGE_NAS_ROOT`
- `MEDIACREATOR_STORAGE_EMBEDDINGS_ROOT`
- `MEDIACREATOR_STORAGE_VAES_ROOT`
- `MEDIACREATOR_COMFYUI_ROOT`
- `MEDIACREATOR_COMFYUI_BASE_URL`
- `MEDIACREATOR_COMFYUI_WORKFLOWS_ROOT`
- `MEDIACREATOR_BLENDER_BIN`
- `MEDIACREATOR_WORKER_CONCURRENCY`

## Current truth

- MediaCreator is single-user mode only in this rebuild.
- The database container exists, and Phase 04 introduces the first migration-backed schema.
- The worker now polls PostgreSQL, claims queued rows with `FOR UPDATE SKIP LOCKED`, and records job history.
- Generation capability is reported through `/api/v1/system/status` and stays unavailable or partial until ComfyUI, workflows, and NAS model roots are detected.
- The landing page and health endpoint are truthful placeholders until later phases add more surface area.

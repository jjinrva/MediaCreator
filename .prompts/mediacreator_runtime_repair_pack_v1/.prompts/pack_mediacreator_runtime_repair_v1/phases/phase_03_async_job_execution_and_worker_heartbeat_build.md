# Phase 03 build — async job execution and worker heartbeat

## Goal
Use the worker for long-running work and expose worker liveness.

## Exact decisions
- Remove inline `run_worker_once()` calls from request handlers.
- Keep the existing worker process and jobs table.
- Return `202 Accepted` for queued long-running jobs.
- Add a `service_heartbeats` table for worker liveness.
- Expose latest job identifiers and progress fields in screen payloads.
- Do not add websockets; use polling.

## Files to inspect and edit
- new migration under `apps/api/alembic/versions/`
- `apps/api/app/models/*` for heartbeat model
- `apps/worker/src/mediacreator_worker/main.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/api/routes/exports.py`
- `apps/api/app/api/routes/lora.py`
- `apps/api/app/api/routes/video.py`
- `apps/api/app/schemas/jobs.py`
- `apps/api/app/schemas/exports.py`
- `apps/api/app/schemas/lora.py`
- `apps/api/app/schemas/video.py`
- `apps/api/app/services/exports.py`
- `apps/api/app/services/lora_training.py`
- `apps/api/app/services/video_render.py`
- `apps/api/app/services/system_runtime.py`
- diagnostics/status tests

## Exact steps
1. Add a heartbeat table/model with one row per service name.
2. Make the worker write/update its heartbeat on every poll cycle.
3. Remove `run_worker_once()` from:
   - preview export route
   - reconstruction route
   - LoRA training route
   - video render route
4. Return queue-only `202` responses that include `job_public_id`, `status`, `step_name`, and `progress_percent`.
5. Add latest job public IDs to:
   - export payload
   - reconstruction payload
   - LoRA training payload
   - video screen payload
6. Add worker health to `/api/v1/system/status` and diagnostics.

## Required code patterns
Use:
- `CODE_EXAMPLES.md` section 1
- `CODE_EXAMPLES.md` section 3

## Do not do
- do not execute Blender, reconstruction, LoRA, or video work inline in the HTTP request
- do not replace the worker with another queue technology
- do not hide stale worker state

## Done when
- the POST routes queue and return 202
- a separate worker process is required to move jobs forward
- worker heartbeat is visible from system status
- payloads expose latest job IDs and progress metadata

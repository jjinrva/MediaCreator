# Runtime Repair Phase 03

## Status

Implemented. Paired verification not yet run in this report.

## Goal

Move long-running work to the existing worker, stop running jobs inline inside HTTP requests, and expose truthful worker liveness plus job progress metadata.

## Changes made

- added [service_heartbeat.py](/opt/MediaCreator/apps/api/app/models/service_heartbeat.py) and migration [0008_service_heartbeats_foundation.py](/opt/MediaCreator/apps/api/alembic/versions/0008_service_heartbeats_foundation.py) for one heartbeat row per service name
- updated [jobs.py](/opt/MediaCreator/apps/api/app/services/jobs.py) with:
  - heartbeat upsert/read helpers
  - worker heartbeat payload generation with `ready` / `stale` / `missing` state
- updated the worker loop in [main.py](/opt/MediaCreator/apps/worker/src/mediacreator_worker/main.py) so it writes a `worker` heartbeat every poll cycle before claiming jobs
- removed inline `run_worker_once()` execution from:
  - [exports.py](/opt/MediaCreator/apps/api/app/api/routes/exports.py)
  - [lora.py](/opt/MediaCreator/apps/api/app/api/routes/lora.py)
  - [video.py](/opt/MediaCreator/apps/api/app/api/routes/video.py)
- added queue-only `202 Accepted` responses through [jobs.py](/opt/MediaCreator/apps/api/app/schemas/jobs.py) for long-running POST routes:
  - `job_public_id`
  - `status`
  - `step_name`
  - `progress_percent`
  - `detail`
- extended payload schemas and builders so latest job identifiers and progress metadata are exposed in:
  - [exports.py](/opt/MediaCreator/apps/api/app/schemas/exports.py)
  - [lora.py](/opt/MediaCreator/apps/api/app/schemas/lora.py)
  - [video.py](/opt/MediaCreator/apps/api/app/schemas/video.py)
  - [exports.py](/opt/MediaCreator/apps/api/app/services/exports.py)
  - [lora_training.py](/opt/MediaCreator/apps/api/app/services/lora_training.py)
  - [video_render.py](/opt/MediaCreator/apps/api/app/services/video_render.py)
- updated [system.py](/opt/MediaCreator/apps/api/app/schemas/system.py), [system_runtime.py](/opt/MediaCreator/apps/api/app/services/system_runtime.py), [system.py](/opt/MediaCreator/apps/api/app/api/routes/system.py), and [diagnostics.py](/opt/MediaCreator/apps/api/app/services/diagnostics.py) so `/api/v1/system/status` and diagnostics expose worker health truthfully
- updated migration, jobs, generation-provider, diagnostics, export, reconstruction, texture, video, and LoRA API tests to prove:
  - the routes queue instead of completing inline
  - a separate worker cycle is required to move jobs forward
  - worker heartbeat state is visible

## Result

- preview export, reconstruction, LoRA training, and video render routes now queue work and return `202`
- jobs remain queued until the worker claims them
- worker liveness is available from `/api/v1/system/status` and diagnostics
- export, reconstruction, LoRA, and video payloads now expose latest job ids plus progress fields

## Pre-verification evidence

- `cd /opt/MediaCreator/apps/api && .venv/bin/ruff check app tests` passed
- `cd /opt/MediaCreator/apps/api && .venv/bin/python -m pytest tests/test_db_migrations.py tests/test_jobs_service.py` passed
- `cd /opt/MediaCreator/apps/api && .venv/bin/python -m pytest tests/test_generation_provider.py tests/test_system_runtime_api.py tests/test_exports_api.py tests/test_blender_export_api.py tests/test_texture_pipeline_api.py tests/test_reconstruction_api.py tests/test_video_render_api.py tests/test_lora_training_api.py` passed

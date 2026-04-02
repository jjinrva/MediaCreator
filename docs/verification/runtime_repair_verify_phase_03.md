# Runtime Repair Phase 03 Verification

## Status

PASS

## Inline-worker code gate

Command:

```bash
rg -n "run_worker_once" \
  /opt/MediaCreator/apps/api/app/api/routes/exports.py \
  /opt/MediaCreator/apps/api/app/api/routes/lora.py \
  /opt/MediaCreator/apps/api/app/api/routes/video.py || true
```

Result:
- no matches

This confirms the long-running HTTP routes no longer call `run_worker_once()` inline.

## Test gates

Command:

```bash
cd /opt/MediaCreator/apps/api
.venv/bin/python -m pytest \
  tests/test_db_migrations.py \
  tests/test_jobs_service.py \
  tests/test_system_runtime_api.py \
  tests/test_blender_export_api.py \
  tests/test_texture_pipeline_api.py \
  tests/test_reconstruction_api.py \
  tests/test_video_render_api.py \
  tests/test_lora_training_api.py
```

Result:
- `15` tests passed

Verified by that suite:
- migration includes the heartbeat table
- job service exposes queued vs running vs completed/failed distinctly
- system status and diagnostics expose worker heartbeat state
- preview export, reconstruction, LoRA training, and video render routes return `202`
- route tests prove the jobs are initially queued and require a separate worker cycle to finish

## Worker gates

Used an isolated temporary PostgreSQL database so the worker start/stop checks did not disturb the main MediaCreator runtime.

### Queue job with worker offline

Seeded a migrated temp DB and enqueued one `noop` job, then probed through FastAPI `TestClient`.

Observed before starting the worker:
- `/api/v1/jobs/{job_public_id}` returned `200`
- job `status` was `queued`
- job `step_name` was `queued`
- job `progress_percent` was `0`
- `/api/v1/system/status` reported:
  - `worker.status = "offline"`

### Start worker and confirm progress

Command:

```bash
cd /opt/MediaCreator
MEDIACREATOR_DATABASE_URL=<temp-db-url> scripts/run_worker.sh
```

Observed after starting the worker:
- worker logged `Worker cycle result: completed`
- `/api/v1/system/status` reported:
  - `worker.status = "ready"`
- `/api/v1/jobs/{job_public_id}` reported:
  - `status = "completed"`
  - `step_name = "completed"`
  - `progress_percent = 100`

The worker was then stopped cleanly and the temp DB was dropped.

## Conclusion

Phase 03 is verified complete:
- long-running routes queue instead of running inline
- queued jobs are distinguishable from running/completed jobs
- worker heartbeat is present and visible
- worker offline-to-ready state is observable through system status

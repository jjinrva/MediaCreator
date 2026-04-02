# Operator runbook

## Morning startup

Run from `/opt/MediaCreator`:

```bash
make bootstrap
docker compose -f infra/docker-compose.yml up -d postgres
make dev
```

Expected local endpoints:

- web: `http://<current-lan-host>:3000`
- API: `http://127.0.0.1:8010`
- health: `http://127.0.0.1:8010/health`

The services bind on `0.0.0.0` by default. Use the machine's current LAN hostname or IP in the browser, and use `127.0.0.1` for on-box API health checks.

## Actual operator flow

- photoset upload and QC are immediate; accepted and rejected counts come back in the upload response
- base character creation is immediate once at least one accepted entry exists
- preview export, high-detail reconstruction, LoRA training, and controlled video render are queued jobs
- each queued route returns a `job_public_id`; the web UI follows that through `/api/v1/jobs/{job_public_id}`
- if `/api/v1/system/status` reports the `worker` heartbeat as `offline` or `stale`, queued jobs will not progress until the worker is started again
- when troubleshooting the character detail page, check `/studio/diagnostics` or `GET /api/v1/system/status` before assuming the queue is broken

## Required runtime directories

- NAS root: `MEDIACREATOR_STORAGE_NAS_ROOT`
- scratch root: `MEDIACREATOR_STORAGE_SCRATCH_ROOT`
- ComfyUI workflows: `workflows/comfyui`
- model roots:
  - checkpoints
  - LoRAs
  - embeddings
  - VAEs

Use `/studio/settings` or `GET /api/v1/system/status` to confirm the active resolved paths before operator use.

## Verification before use

Run from `/opt/MediaCreator`:

```bash
make test-api
make test-web
make lint
make typecheck
```

Current final verification artifacts:

- `docs/verification/final_verify_matrix.md`
- `docs/verification/final_verify_matrix.json`

## What is working

- photoset upload, QC, and prepared-image storage
- character creation and reloadable character detail
- persisted body, pose, and face parameter editing
- Blender-backed preview export and high-detail reconstruction prep contract
- texture/material fidelity reporting
- LoRA dataset creation and truthful local training capability reporting
- wardrobe catalog creation from photo and prompt
- motion assignment and controlled Blender video rendering
- standalone generation workspace with visible `@character` expansion and registry-backed model references
- runtime settings and live diagnostics screens

## What remains intentionally deferred

- real final media generation still depends on a responding ComfyUI service plus real NAS-backed checkpoint and VAE files
- real local LoRA training still depends on AI Toolkit being installed
- multi-user auth, permissions, and role management are intentionally out of scope for this single-user rebuild

## Test-harness note

`apps/web/playwright.config.js` runs Playwright with one worker on purpose. The local Next.js dev server was intermittently unstable under fully parallel browser workers during the full regression sweep.

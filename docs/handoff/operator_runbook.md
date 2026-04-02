# Operator runbook

## Morning startup

Run from `/opt/MediaCreator`:

```bash
make bootstrap
docker compose -f infra/docker-compose.yml up -d postgres
make dev
```

Expected local endpoints:

- web: `http://10.0.0.102:3000`
- API: `http://10.0.0.102:8010`
- health: `http://10.0.0.102:8010/health`

The services bind on `0.0.0.0` by default. Use the `10.0.0.102` URLs in the browser and operator checks.

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

# MediaCreator

MediaCreator is a single-user rebuild that starts with one web app, one API app, one worker app, shared docs, and a fixed folder contract for the later phases.

## Prerequisites

- Linux
- `bash`
- `curl`
- `docker`
- `docker compose`
- `tar`
- `make`
- Python 3.12

Node.js 22 LTS and `pnpm` are bootstrapped locally into `infra/` by `make install`, so they do not need to be preinstalled system-wide.

## Bootstrap

1. Copy `.env.example` to `.env` if you want to override the defaults.
2. Run:

```bash
make bootstrap
```

That command:

- downloads a local Node.js 22 LTS toolchain into `infra/node`
- installs a local `pnpm` runtime into `infra/pnpm`
- resolves the pnpm workspace at the repo root
- creates Python virtual environments for `apps/api` and `apps/worker`
- installs the API and worker dependencies in editable mode

PostgreSQL is started separately through Docker Compose, or automatically by `make dev`.

## NAS and scratch requirements

- `MEDIACREATOR_STORAGE_NAS_ROOT` must point at the mounted NAS location for canonical long-lived assets.
- `MEDIACREATOR_STORAGE_SCRATCH_ROOT` must point at fast local disk for short-lived working files and caches.
- ComfyUI model roots stay NAS-backed by default for checkpoints, LoRAs, embeddings, and VAEs.
- If the NAS mount is missing, MediaCreator still boots in degraded local-only mode and reports that truthfully through the runtime health data.

## Folder structure

- `apps/web` — Next.js App Router frontend
- `apps/api` — FastAPI HTTP API
- `apps/worker` — dedicated Python worker bootstrap
- `packages/shared-types` — shared TypeScript package for frontend workspace code
- `docs` — phase reports, verification reports, architecture notes, and capture guides
- `infra` — local toolchain bootstrap assets and future infrastructure support files
- `scripts` — canonical shell entrypoints called by `make`
- `storage` — tracked placeholder for future asset storage roots
- `workflows` — versioned local workflow definitions, including `workflows/comfyui`
- `.prompts` — rebuild pack inputs
- `experts` — shared expert guidance for each phase

## Start PostgreSQL only

```bash
docker compose -f infra/docker-compose.yml up -d postgres
```

The Phase 02 local runtime uses PostgreSQL 16 on `127.0.0.1:54329` by default.

## Run the full local stack

```bash
make dev
```

`make dev` starts PostgreSQL if needed, waits for readiness, and then runs the API, web app, and worker from source.

## Run the API

```bash
make api
```

The API exposes a truthful health endpoint at `http://127.0.0.1:8010/health`.

Phase 10 adds:

- `POST /api/v1/photosets` for multi-file upload with original, normalized, and thumbnail artifact creation
- `GET /api/v1/photosets/{photoset_public_id}` for reloadable QC results
- `GET /api/v1/photosets/{photoset_public_id}/entries/{entry_public_id}/artifacts/{variant}` for stored original, normalized, and thumbnail files

Phase 11 adds:

- `POST /api/v1/characters` to create one base character record from a persisted photoset
- `GET /api/v1/characters/{character_public_id}` to load the API-backed character detail route with accepted references and history

Phase 12 adds:

- `GET /api/v1/exports/characters/{character_public_id}` for preview/export scaffold status
- `GET /api/v1/exports/characters/{character_public_id}/preview.glb` for the future preview artifact path
- `GET /api/v1/exports/characters/{character_public_id}/final.glb` for the future final export path

Phase 13 adds:

- `GET /api/v1/body/characters/{character_public_id}` for the canonical numeric body-parameter catalog and current values

Phase 14 adds:

- `PUT /api/v1/body/characters/{character_public_id}` for one canonical body-parameter save path

Phase 15 adds:

- `GET /api/v1/pose/characters/{character_public_id}` for the canonical limb-pose catalog and current values
- `PUT /api/v1/pose/characters/{character_public_id}` for one canonical pose-parameter save path

Phase 16 adds:

- `GET /api/v1/face/characters/{character_public_id}` for the canonical facial-parameter catalog and current values
- `PUT /api/v1/face/characters/{character_public_id}` for one canonical facial-parameter save path

## Generation capability status

Phase 06 treats ComfyUI as a separate local service. MediaCreator does not claim generation is ready until it can detect:

- `MEDIACREATOR_COMFYUI_BASE_URL`
- versioned workflow JSON files under `workflows/comfyui`
- NAS-backed model roots for checkpoints, LoRAs, embeddings, and VAEs
- at least one checkpoint file and one VAE file

Check the current status through:

```bash
curl http://127.0.0.1:8010/api/v1/system/status
```

## Database migrations

Run from the repository root:

```bash
apps/api/.venv/bin/alembic -c apps/api/alembic.ini upgrade head
apps/api/.venv/bin/alembic -c apps/api/alembic.ini downgrade base
```

## Run the web app

```bash
make web
```

The web app serves a truthful front door at `http://127.0.0.1:3000/` and the Phase 07 studio shell at `http://127.0.0.1:3000/studio`.

Phase 08 adds the guided capture route at `http://127.0.0.1:3000/studio/capture-guide`.
Phase 09 adds the canonical character-ingest route at `http://127.0.0.1:3000/studio/characters/new`.
Phase 10 connects that route to the FastAPI photoset upload and QC pipeline.
Phase 11 adds the API-backed character detail route at `http://127.0.0.1:3000/studio/characters/[publicId]`.
Phase 12 turns that detail page into the fixed Overview/Body/Pose/History/Outputs layout with a truthful GLB preview scaffold.
Phase 13 fills the Body section with the API-backed read-only parameter catalog and current numeric values.
Phase 14 turns the Body section into the persisted slider editor and writes history on each committed change.
Phase 15 turns the Pose section into the persisted limb-pose editor and keeps pose history truthful across reloads.
Phase 16 adds the persisted Face section with truthful facial-parameter history and reload behavior.
The web app expects `NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL` to point at the FastAPI service; the default example value is `http://127.0.0.1:8010`.

## Run the worker

```bash
make worker
```

The worker now polls PostgreSQL for queued jobs and claims work with `FOR UPDATE SKIP LOCKED`.

## Capture guide assets

Re-render the tracked Blender onboarding boards with:

```bash
scripts/blender/render_capture_guides.sh
```

That command writes the generic capture-reference PNG files into `docs/capture_guides/assets/`. The matching written guide lives at `docs/capture_guides/capture_guide.md`.

## Photoset upload and QC

The Phase 10 ingest flow uploads files to FastAPI, writes original plus prepared derivatives, and persists QC metrics for reload. You can exercise the API directly with:

```bash
curl -F "photos=@/path/to/photo-1.png" -F "photos=@/path/to/photo-2.png" http://127.0.0.1:8010/api/v1/photosets
```

The first upload downloads the required MediaPipe task bundles into the scratch storage root if they are not already cached.

## Character registry

Phase 11 turns a persisted photoset into one durable character registry row and exposes the same record through the web detail route. You can exercise the API directly with:

```bash
curl -X POST http://127.0.0.1:8010/api/v1/characters \
  -H 'content-type: application/json' \
  -d '{"photoset_public_id":"<photoset-public-id>"}'
```

Repeating that call for the same photoset returns the same character public ID instead of creating a duplicate row.

## Character outputs scaffold

Phase 12 establishes the output destination and the web preview shell without pretending a GLB already exists. You can inspect the current scaffold with:

```bash
curl http://127.0.0.1:8010/api/v1/exports/characters/<character-public-id>
```

If no preview or final export artifact exists yet, the API reports `not-ready` and the GLB file routes return `404`.

## Body parameter catalog

Phase 13 freezes the numeric body contract and exposes it through:

```bash
curl http://127.0.0.1:8010/api/v1/body/characters/<character-public-id>
```

The frozen catalog and ranges are documented in `docs/architecture/body_parameter_contract.md`.

To update one value directly through the API:

```bash
curl -X PUT http://127.0.0.1:8010/api/v1/body/characters/<character-public-id> \
  -H 'content-type: application/json' \
  -d '{"parameter_key":"shoulder_width","numeric_value":1.05}'
```

## Pose parameter catalog

Phase 15 freezes the numeric limb-pose contract and exposes it through:

```bash
curl http://127.0.0.1:8010/api/v1/pose/characters/<character-public-id>
```

The frozen catalog, bone names, axes, and ranges are documented in `docs/architecture/pose_parameter_contract.md`.

To update one pose value directly through the API:

```bash
curl -X PUT http://127.0.0.1:8010/api/v1/pose/characters/<character-public-id> \
  -H 'content-type: application/json' \
  -d '{"parameter_key":"upper_arm_l_pitch_deg","numeric_value":15}'
```

## Face parameter catalog

Phase 16 freezes the numeric facial-parameter contract and exposes it through:

```bash
curl http://127.0.0.1:8010/api/v1/face/characters/<character-public-id>
```

The frozen catalog and Blender mapping targets are documented in `docs/architecture/face_parameter_contract.md`.

To update one facial value directly through the API:

```bash
curl -X PUT http://127.0.0.1:8010/api/v1/face/characters/<character-public-id> \
  -H 'content-type: application/json' \
  -d '{"parameter_key":"jaw_open","numeric_value":0.15}'
```

## Common commands

```bash
make lint
make typecheck
make test-api
make test-web
```

## Intentionally not finished yet

- PostgreSQL and migrations
- durable job foundation only, with no real media pipelines yet
- real ComfyUI image generation execution
- higher-level asset workflows beyond the base registry and history tables
- per-image replacement and richer character creation workflows on top of the new ingest/QC pipeline
- GLB preview and Blender integration
- real facial deformation driven by Blender shape keys
- LoRA training and generation workflows
- wardrobe, motion, and rendering features

Those capabilities are added only by later phases after their paired verification passes.

## Environment contract

Phase 02 documents the runtime contract in:

- `docs/architecture/repo_contract.md`
- `docs/architecture/local_runtime.md`
- `.env.example`

Phase 03 adds the canonical storage contract in `docs/architecture/storage_layout.md`.
Phase 05 adds the queue/runtime contract in `docs/architecture/job_runtime.md`.
Phase 06 adds the ComfyUI capability contract in `docs/architecture/generation_capability.md`.
Phase 07 adds the studio shell contract in `docs/architecture/studio_shell.md`.
Phase 08 adds the capture guide markdown in `docs/capture_guides/capture_guide.md`.
Phase 10 adds the photoset upload and QC API contract in `apps/api/app/api/routes/photosets.py`.
Phase 11 adds the character registry contract in `docs/architecture/character_registry.md`.
Phase 12 adds the character outputs contract in `docs/architecture/character_outputs.md`.
Phase 13 adds the body parameter contract in `docs/architecture/body_parameter_contract.md`.
Phase 15 adds the pose parameter contract in `docs/architecture/pose_parameter_contract.md`.
Phase 16 adds the face parameter contract in `docs/architecture/face_parameter_contract.md`.

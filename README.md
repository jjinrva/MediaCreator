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
The default bind host is `0.0.0.0`; open the web app through the machine's current LAN hostname or IP instead of a fixed address.

## Runtime flow

- bind the API and web server on `0.0.0.0`
- open the browser against the machine's current hostname or LAN IP
- use `127.0.0.1` only for on-box API health checks and internal server-side defaults
- photoset upload and QC return immediately
- base character creation returns immediately after accepted-entry validation
- preview export, high-detail reconstruction, LoRA training, and controlled video render are queued background jobs
- queued job progress comes from `GET /api/v1/jobs/{job_public_id}`
- worker liveness comes from `GET /api/v1/system/status`; if the heartbeat is stale or offline, queued jobs will not advance

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
- `POST /api/v1/exports/characters/{character_public_id}/preview` to queue the preview export job
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

Phase 18 adds:

- `POST /api/v1/exports/characters/{character_public_id}/reconstruction` for the truthful high-detail reconstruction job
- `GET /api/v1/exports/characters/{character_public_id}/detail-prep.json` for the optional detail-prep artifact

Phase 19 adds:

- `GET /api/v1/exports/characters/{character_public_id}/textures/base-color.png` for the persisted base-color texture artifact
- `GET /api/v1/exports/characters/{character_public_id}/textures/refined-color.png` for a future refined texture artifact path

Phase 20 adds:

- `GET /api/v1/lora-datasets/characters/{character_public_id}` for the LoRA dataset status and visible prompt contract
- `POST /api/v1/lora-datasets/characters/{character_public_id}` to build the current dataset version
- `GET /api/v1/lora-datasets/characters/{character_public_id}/manifest.json` for the generated dataset manifest

Phase 21 adds:

- `GET /api/v1/lora/characters/{character_public_id}` for local LoRA training readiness, registry state, and the active model
- `POST /api/v1/lora/characters/{character_public_id}` to queue one AI Toolkit training job when the trainer and dataset are both ready

Phase 22 adds:

- `GET /api/v1/wardrobe` for the closet catalog and AI wardrobe capability summary
- `POST /api/v1/wardrobe/from-photo` to ingest one garment photo into the wardrobe catalog
- `POST /api/v1/wardrobe/from-prompt` to create one prompt-backed wardrobe item
- `GET /api/v1/wardrobe/{wardrobe_public_id}/source-photo` for a stored wardrobe source photo

Phase 23 adds:

- `GET /api/v1/motion` for the local motion library, current character assignments, and import guidance
- `PUT /api/v1/motion/characters/{character_public_id}` to assign one motion clip to one character

Phase 24 adds:

- `GET /api/v1/video` for the controlled video render screen contract
- `POST /api/v1/video/characters/{character_public_id}/render` to render one rig-driven MP4 clip from the assigned motion
- `GET /api/v1/video/assets/{video_asset_public_id}.mp4` for the persisted rendered MP4

Phase 25 adds:

- `GET /api/v1/generation` for the standalone generation workspace contract
- `POST /api/v1/generation/expand` for visible `@character` prompt expansion
- `POST /api/v1/generation/requests` to store one generation request with expanded prompt and registry-backed model references
- `GET /api/v1/generation/external-loras/search` and `POST /api/v1/generation/external-loras/import` for the opt-in Civitai discovery/import path

Phase 26 adds:

- `GET /api/v1/system/diagnostics` for live end-to-end checks across ingest, body/pose persistence, preview/export availability, LoRA readiness, and generation readiness

Long-running POST routes return `202 Accepted` and a `job_public_id`. Follow those jobs with:

```bash
curl http://127.0.0.1:8010/api/v1/jobs/<job-public-id>
```

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

The web app serves a truthful front door at `http://<current-lan-host>:3000/` and the Phase 07 studio shell at `http://<current-lan-host>:3000/studio`.

Phase 08 adds the guided capture route at `http://<current-lan-host>:3000/studio/capture-guide`.
Phase 09 adds the canonical character-ingest route at `http://<current-lan-host>:3000/studio/characters/new`.
Phase 10 connects that route to the FastAPI photoset upload and QC pipeline.
Phase 11 adds the API-backed character detail route at `http://<current-lan-host>:3000/studio/characters/[publicId]`.
Phase 12 turns that detail page into the fixed Overview/Body/Pose/History/Outputs layout with a truthful GLB preview scaffold and a queued preview-generation progress card after base character creation.
Phase 13 fills the Body section with the API-backed read-only parameter catalog and current numeric values.
Phase 14 turns the Body section into the persisted slider editor and writes history on each committed change.
Phase 15 turns the Pose section into the persisted limb-pose editor and keeps pose history truthful across reloads.
Phase 16 adds the persisted Face section with truthful facial-parameter history and reload behavior.
Phase 18 adds the high-detail reconstruction control, queues it as background work, and reports the current detail level truthfully in the Outputs section.
Phase 19 extends the Outputs section again so it reports the current texture fidelity and the texture artifact state truthfully.
Phase 20 adds a LoRA Dataset section that shows the current prompt handle, visible tags, expansion string, and dataset build status.
Phase 21 adds a LoRA Training section that reports whether AI Toolkit is actually available, disables training when it is not, and queues the training job when the runtime is ready.
Phase 22 adds the wardrobe catalog route at `http://<current-lan-host>:3000/studio/wardrobe` with separate photo-ingest and prompt-backed creation paths plus a reloadable closet list.
Phase 23 adds the motion library route at `http://<current-lan-host>:3000/studio/motion` so a real character can be assigned one reusable local action clip.
Phase 24 adds the controlled video route at `http://<current-lan-host>:3000/studio/video` so the assigned motion can be queued, rendered into a truthful MP4, and replayed after reload.
Phase 25 adds the standalone generation workspace at `http://<current-lan-host>:3000/studio/generate` so prompts, visible `@character` expansion, and registry-backed LoRA references can be staged without crossing into the 3D editing routes.
Phase 26 adds the runtime settings route at `http://<current-lan-host>:3000/studio/settings` and the live diagnostics route at `http://<current-lan-host>:3000/studio/diagnostics`.
The web app expects `NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL` to point at the FastAPI service; the default example value is `http://127.0.0.1:8010`.

## Final verification

Run the final local verification sweep from the repository root with:

```bash
make test-api
make test-web
make lint
make typecheck
```

The Phase 26 final verification artifacts live at:

- `docs/verification/final_verify_matrix.md`
- `docs/verification/final_verify_matrix.json`
- `docs/handoff/operator_runbook.md`
- `docs/handoff/overnight_acceptance_report.md`

The Playwright suite is pinned to one worker in `apps/web/playwright.config.js` so the Next.js dev server stays stable during the full local browser sweep.

## Run the worker

```bash
make worker
```

The worker polls PostgreSQL for queued jobs, claims work with `FOR UPDATE SKIP LOCKED`, and updates the `worker` heartbeat that the web app surfaces in progress cards and diagnostics.

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

Phase 18 extends that same payload with the current high-detail reconstruction level, the chosen reconstruction strategy, the optional detail-prep artifact, and the reconstruction job status. The exact path is documented in `docs/architecture/high_detail_3d_path.md`.

Phase 19 extends the same payload again with current texture fidelity plus base/refined texture artifact metadata. The texture/material path is documented in `docs/architecture/texture_material_fidelity.md`.

## LoRA dataset contract

Phase 20 adds the first versioned LoRA dataset folder and prompt expansion contract. Build or inspect it with:

```bash
curl http://127.0.0.1:8010/api/v1/lora-datasets/characters/<character-public-id>

curl -X POST http://127.0.0.1:8010/api/v1/lora-datasets/characters/<character-public-id>
```

The manifest route is:

```bash
curl http://127.0.0.1:8010/api/v1/lora-datasets/characters/<character-public-id>/manifest.json
```

The exact dataset and prompt-handle rules are documented in `docs/architecture/lora_dataset_contract.md`.

## LoRA training registry

Phase 21 adds the first NAS-backed LoRA model registry plus truthful local AI Toolkit readiness reporting:

```bash
curl http://127.0.0.1:8010/api/v1/lora/characters/<character-public-id>

curl -X POST http://127.0.0.1:8010/api/v1/lora/characters/<character-public-id>
```

If AI Toolkit is missing, the GET route reports `status: unavailable` and the POST route refuses to fake a pass. The registry and activation contract are documented in `docs/architecture/lora_training_registry.md`.

## Wardrobe catalog

Phase 22 adds the first reusable closet catalog. Create or inspect wardrobe items with:

```bash
curl http://127.0.0.1:8010/api/v1/wardrobe

curl -X POST http://127.0.0.1:8010/api/v1/wardrobe/from-prompt \
  -H 'content-type: application/json' \
  -d '{"label":"Brown jacket","garment_type":"jacket","material":"leather","base_color":"brown","prompt_text":"brown leather jacket"}'
```

The photo path is multipart:

```bash
curl -X POST http://127.0.0.1:8010/api/v1/wardrobe/from-photo \
  -F "photo=@/path/to/garment.png" \
  -F "label=Black tank top" \
  -F "garment_type=tank top" \
  -F "material=cotton" \
  -F "base_color=black"
```

The catalog and asset-splitting rules are documented in `docs/architecture/wardrobe_catalog_contract.md`.

## Motion library

Phase 23 adds the first local motion library and character-assignment path:

```bash
curl http://127.0.0.1:8010/api/v1/motion

curl -X PUT http://127.0.0.1:8010/api/v1/motion/characters/<character-public-id> \
  -H 'content-type: application/json' \
  -d '{"motion_public_id":"<motion-public-id>"}'
```

The seeded library contains `idle`, `walk`, `jump`, `sit`, and `turn`. The contract is documented in `docs/architecture/motion_contract.md`.

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
- additional media pipelines beyond the verified preview, reconstruction, texture, dataset, and local-LoRA registry paths
- real ComfyUI image generation execution
- higher-level asset workflows beyond the base registry and history tables
- per-image replacement and richer character creation workflows on top of the new ingest/QC pipeline
- real facial deformation driven by Blender shape keys
- full LoRA-activated image generation workflows
- controlled rendered animation output

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
Phase 21 adds the LoRA training registry contract in `docs/architecture/lora_training_registry.md`.
Phase 22 adds the wardrobe catalog contract in `docs/architecture/wardrobe_catalog_contract.md`.
Phase 23 adds the motion contract in `docs/architecture/motion_contract.md`.

# Patch scope and file map

This file gives the exact first-pass file areas Codex must inspect before editing.

## Phase 01 — backend ingest progress and person-first routing

Inspect first:

- `apps/api/app/api/routes/photosets.py`
- `apps/api/app/services/photo_prep.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/api/routes/jobs.py`
- any photoset/job schemas or models adjacent to those files

## Phase 02 — frontend intake truth, label, and thumbnail preview

Inspect first:

- `apps/web/app/studio/characters/new/page.tsx`
- `apps/web/components/character-import/CharacterImportIngest.tsx`
- adjacent intake components under `apps/web/components/character-import`
- any shared status/progress components reused on the character flow

## Phase 03 — preprocessing derivatives and dataset manifests

Inspect first:

- `apps/api/app/services/photo_prep.py`
- `apps/api/app/services/lora_dataset.py`
- any storage/lineage helpers used by those services

## Phase 04 — base character creation and saved 3D output

Inspect first:

- `apps/api/app/services/characters.py`
- `apps/api/app/api/routes/characters.py`
- `apps/api/app/api/routes/exports.py`
- `apps/api/app/services/reconstruction.py`
- `apps/api/app/services/blender_runtime.py`
- `apps/web/app/studio/characters/[publicId]/page.tsx`
- `apps/web/components/glb-preview/GlbPreview.tsx`

## Phase 05 — LoRA training, registry, and proof generation

Inspect first:

- `apps/api/app/services/lora_dataset.py`
- `apps/api/app/services/lora_training.py`
- `apps/api/app/api/routes/lora.py`
- `apps/api/app/models/models_registry.py`
- generation routes/services that resolve active LoRA artifacts

## Phase 06 — end-to-end acceptance and truth gates

Inspect first:

- repo test directories for API/UI/e2e coverage
- any scripts used for artifact verification
- status/output models and UI components that mark jobs complete

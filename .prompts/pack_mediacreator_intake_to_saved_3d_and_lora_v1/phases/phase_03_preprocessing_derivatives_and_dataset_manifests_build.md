# Phase 03 build — Preprocessing derivatives and dataset manifests

## Phase goal

Write the exact derivative assets and manifests needed for downstream body/3D and LoRA work.

## Experts Codex must use for this phase

- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/DIFFUSION_COMFYUI_AND_LORA_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

## Exact chosen path

- Preserve originals.
- Write one normalized derivative for downstream use on every person-qualified image.
- Write one background-removed derivative for every `body_only` or `both` image.
- Write one conservative LoRA-normalized derivative for every `lora_only` or `both` image.
- Create explicit manifests so downstream services never have to infer which files belong to which purpose.

## Exact stack and libraries

- Pillow
- OpenCV
- the repo’s existing storage/lineage layer
- `rembg` or the exact existing segmentation helper already present in the repo if one exists
- AI Toolkit-compatible image+caption dataset structure

### Source IDs for this phase
S10, S11, S13, S14

## Exact file areas

Start with these files:

- `apps/api/app/services/photo_prep.py`
- `apps/api/app/services/lora_dataset.py`

Inspect adjacent storage/lineage helpers only as needed.

## Ordered steps

### Step 1 — normalized derivative for all person-qualified images

For every image where `has_person == true`, write a normalized derivative with:

- orientation normalized
- color profile normalized to sRGB
- no aggressive retouch
- no upscaling

**Verification immediately after Step 1**
- add tests that assert normalized derivatives exist and are lineage-linked

### Step 2 — background-removed body derivative

For every image bucketed as `body_only` or `both`, write a body derivative with the background removed or alpha-masked.

Rules:
- preserve the original
- preserve the normalized derivative
- do not overwrite either
- keep the body derivative as the exact downstream input for body/3D preparation

**Verification immediately after Step 2**
- add tests that assert body derivatives exist only for body-qualified buckets
- verify alpha/background-removed outputs are recorded in metadata

### Step 3 — conservative LoRA derivative

For every image bucketed as `lora_only` or `both`, write a LoRA derivative.

Allowed changes:
- mild exposure normalization
- mild white-balance normalization
- mild global contrast normalization

Forbidden changes:
- face beautification
- identity reshaping
- heavy sharpen / denoise
- hallucinated repair

Do not treat this derivative as a way to rescue unusable images. Images that still fail LoRA gates remain excluded.

**Verification immediately after Step 3**
- add tests that LoRA derivatives exist only for LoRA-qualified buckets
- assert rejected images do not silently enter the LoRA manifest

### Step 4 — explicit manifests

Write explicit manifests with:
- source asset IDs
- derivative paths
- bucket
- reason codes
- caption or caption seed data for LoRA-qualified images

Create one manifest shape for photoset derivatives and one versioned manifest shape for LoRA dataset construction.

**Verification immediately after Step 4**
- add tests that manifests exist and point only to allowed bucket members

## Pass/fail criteria

### PASS
- originals are preserved
- body derivatives exist only where body routing allows them
- LoRA derivatives exist only where LoRA routing allows them
- manifests are explicit and reloadable
- rejected assets never leak into the LoRA manifest

### FAIL
- derivatives overwrite originals
- body derivatives are missing for body-qualified images
- rejected or body-only no-face images leak into the LoRA manifest
- no lineage links exist

## Deliverables

- normalized derivative path
- body derivative path
- LoRA derivative path
- derivative manifest contract
- targeted derivative/manifest tests

## Forbidden scope

- do not train the LoRA in this phase
- do not create the character in this phase
- do not replace the selected segmentation approach with a new unrelated stack

## Documentation Codex must update in this phase

- `docs/phase_reports/intake_saved_outputs_phase_03.md`
- `docs/verification/intake_saved_outputs_phase_03_verify.md`
- `docs/architecture/intake_derivative_contract.md`

## Exit condition

The phase may stop only when derivative creation and manifest creation are both testable and verified by the paired verify file.

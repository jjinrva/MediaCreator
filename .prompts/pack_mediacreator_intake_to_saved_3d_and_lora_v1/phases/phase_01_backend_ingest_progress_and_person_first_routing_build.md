# Phase 01 build — Backend ingest progress and person-first routing

## Phase goal

Convert photoset ingest into a truthful backend flow that:

- accepts a required character label,
- allows duplicate labels,
- writes uploads without loading the whole photoset into memory at once,
- exposes live ingest/classification progress through the existing job/status model,
- classifies every image into `lora_only`, `body_only`, `both`, or `rejected`,
- never rejects a body-capable image solely because no face is visible.

## Experts Codex must use for this phase

- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

## Exact chosen path

- Keep `POST /api/v1/photosets` as the canonical intake entry point.
- Require `character_label` on that route.
- Allow duplicate labels; do not impose uniqueness at the label level.
- Stream or chunk file writes to storage. Do not use one `await upload.read()` over the full file if that is the current implementation.
- Create a real ingest/QC job record and update it with stage names and counts.
- Separate LoRA suitability from body suitability.
- Persist all classification fields so the frontend can reload without recomputing anything in the browser.

## Exact stack and libraries

- FastAPI `UploadFile`
- SQLAlchemy
- Pillow
- MediaPipe Face Landmarker
- MediaPipe Pose Landmarker
- OpenCV
- existing jobs table / job polling path

### Source IDs for this phase
S05, S06, S07, S08, S09, S10, S11

## Exact file areas

Start with these files:

- `apps/api/app/api/routes/photosets.py`
- `apps/api/app/services/photo_prep.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/api/routes/jobs.py`

Inspect adjacent schemas and models only as needed after those files.

## Ordered steps

### Step 1 — require the label at ingest start

Add `character_label` to the canonical intake request contract.

Rules:
- trim leading/trailing whitespace
- reject empty labels
- do not reject duplicate labels
- persist the label on the photoset record for later character creation

**Verification immediately after Step 1**
- add or update an API test that rejects an empty label
- add or update an API test that allows a duplicate label used on a different photoset

### Step 2 — stop reading the entire upload into memory

Replace any whole-file eager read path with a streaming or chunked write path.

Rules:
- validate image count before processing
- validate per-file size and MIME type
- write originals safely to storage
- keep the first implementation focused on images only

**Verification immediately after Step 2**
- add an API test that uploads multiple files and proves the request succeeds
- add a validation test for count and size limits
- document the chosen limits in the phase report

### Step 3 — create truthful ingest/QC job progress

Create or reuse a real job record for photoset ingest.

Required stage names:
- `upload_received`
- `normalizing`
- `person_check`
- `qc_metrics`
- `classification`
- `derivative_write`
- `complete`
- `failed`

Required counters:
- total files
- processed files
- bucket counts

Do not mark the job complete until all persisted photoset entries and derivatives for this phase are actually written.

**Verification immediately after Step 3**
- add an API test that polls the job record and sees ordered stage transitions
- add a test that confirms `complete` is not set before all entry records exist

### Step 4 — implement person-first classification and explicit buckets

For every image, evaluate:

- `has_person`
- `face_detected`
- `body_detected`
- `blur_score`
- `exposure_score`
- `framing_label`
- `occlusion_label`
- `resolution_ok`

Then persist:

- `usable_for_lora`
- `usable_for_body`
- `bucket`
- `reason_codes`
- `reason_messages`

Bucket rules:
- non-person images => `rejected`
- LoRA requires face evidence and stricter quality gating
- body requires body evidence and a more permissive blur threshold
- if both pass => `both`
- if only body passes => `body_only`
- if only LoRA passes => `lora_only`

Do not use one single blur threshold for both purposes.

**Verification immediately after Step 4**
- add a test fixture or mock path for:
  - portrait usable for LoRA only
  - body shot usable for body only with no face
  - image usable for both
  - non-person image rejected
- assert exact bucket values and reason codes

### Step 5 — persist reloadable per-entry status

The photoset API response and reload endpoint must return stable per-entry classification data without recomputing in the browser.

**Verification immediately after Step 5**
- add an API reload test that fetches the same photoset twice and gets stable bucket/reason values

## Pass/fail criteria

### PASS
- label is required and duplicates are allowed
- upload handling is bounded and no longer depends on full-file eager reads
- ingest progress exposes real stages and counts
- body-only no-face images can land in `body_only`
- per-entry buckets and reasons are persisted and reloadable

### FAIL
- empty label is accepted
- duplicate label is rejected
- the job record lacks stage/count truth
- one blur threshold still drives both LoRA and body decisions
- bucket/reason state disappears on reload

## Deliverables

- patched photoset route
- patched photo prep service
- truthful ingest progress state
- persisted person-first classification buckets
- targeted API tests

## Forbidden scope

- do not build the frontend in this phase
- do not add websockets
- do not create manual curation tooling yet
- do not change Blender or LoRA runtime code yet
- do not continue if classification still rejects body-only no-face images

## Documentation Codex must update in this phase

- `docs/phase_reports/intake_saved_outputs_phase_01.md`
- `docs/verification/intake_saved_outputs_phase_01_verify.md`
- any small architecture note needed for the ingest/job contract

## Exit condition

The phase may stop only when all Step 1–5 verification hooks exist and the paired verify file can prove them honestly.

# Phase 10 build — Photo QC and preparation pipeline

## Goal

Normalize uploaded images, compute objective QC signals, and persist original plus prepared derivatives so later 3D and LoRA phases use the best possible inputs.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- FastAPI UploadFile
- Pillow
- MediaPipe Face Landmarker
- MediaPipe Pose Landmarker
- OpenCV
- NumPy

### Source IDs to use for this phase
S09, S21, S22, S23, S24



## Files and directories this phase is allowed to create or modify first

- apps/api/app/services/photo_prep.py
- apps/api/app/api/routes/photosets.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create an upload endpoint that receives multiple photos with `UploadFile`, stores originals, normalizes orientation with Pillow, creates thumbnails, and writes storage metadata rows for each artifact.

### Step 2
Run QC on each normalized image. Compute at minimum: face detected yes/no, body landmarks detected yes/no, blur heuristic, exposure heuristic, and a simple framing label. Store the metrics and a pass/warn/fail decision.

### Step 3
Persist the QC report and prepared derivatives so the web app can reload the ingest page and show the same status without recomputing everything in the browser.

### Step 4
Do not discard rejected images silently. Keep them visible with failure reasons. The user should be able to replace them.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_10.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- upload endpoint
- prep service
- QC storage
- reloadable QC API

## What Codex must not do in this phase


- Do not create parallel implementations of the same concept.
- Do not add auth or multi-user logic in this phase unless the phase explicitly says to create future-ready fields only.
- Do not seed runtime screens with demo/sample data.
- Do not change the chosen stack.
- Do not continue to the next phase until this phase passes verify.


## Exit condition for the build phase

The build phase may stop only when:
1. the phase deliverables exist,
2. the changed code is coherent,
3. the paired verify file has enough hooks to test the phase honestly,
4. `docs/phase_reports/phase_10.md` is updated with exact commands and results.

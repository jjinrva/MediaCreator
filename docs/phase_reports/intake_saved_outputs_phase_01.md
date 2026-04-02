# Phase
`phase_01_backend_ingest_progress_and_person_first_routing`

## Scope
Backend-only intake changes for required labels, bounded upload staging, persisted bucketed QC, and truthful ingest job progress.

## Files changed
- `apps/api/app/api/routes/jobs.py`
- `apps/api/app/api/routes/photosets.py`
- `apps/api/app/models/photoset_entry.py`
- `apps/api/app/schemas/jobs.py`
- `apps/api/app/schemas/photosets.py`
- `apps/api/app/services/characters.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/services/photo_prep.py`
- `apps/api/alembic/versions/0009_photoset_ingest_truth_and_buckets.py`
- `apps/api/tests/test_photosets_api.py`
- `apps/api/tests/test_characters_api.py`
- `apps/api/tests/test_photosets_intake_and_classification.py`
- `apps/api/tests/test_photoset_job_progress.py`

## Implementation summary
- Required `character_label` on `POST /api/v1/photosets`, trimmed it before persistence, and left duplicate labels allowed.
- Replaced whole-request `await upload.read()` intake with staged chunk writes using `UploadFile` and explicit limits.
- Documented and enforced Phase 01 intake limits:
  - max files per photoset: `32`
  - max per-file upload size: `20971520` bytes (`20 MiB`)
  - allowed MIME types: `image/jpeg`, `image/png`, `image/webp`
- Added a real `photoset-ingest` job payload and persisted stage/count updates through the existing jobs table and `/api/v1/jobs/{publicId}`.
- Implemented person-first classification with exclusive persisted buckets:
  - `lora_only`
  - `body_only`
  - `both`
  - `rejected`
- Split blur/exposure gating for LoRA vs body eligibility.
  - `MIN_BLUR_FOR_LORA = 120.0`
  - `MIN_BLUR_FOR_BODY = 70.0`
- Persisted reloadable entry fields:
  - `bucket`
  - `usable_for_lora`
  - `usable_for_body`
  - `reason_codes`
  - `reason_messages`
  - expanded `qc_metrics` including `has_person`, `body_detected`, `occlusion_label`, and `resolution_ok`
- Kept accepted-entry compatibility for downstream character flows by treating non-`rejected` buckets as accepted.

## Verification hooks added
- `apps/api/tests/test_photosets_intake_and_classification.py`
- `apps/api/tests/test_photoset_job_progress.py`
- persisted ingest job stage history in `GET /api/v1/jobs/{job_public_id}`
- reload proof via `GET /api/v1/photosets/{photoset_public_id}`

## Known limitations
- The backend now persists truthful ingest stages and counts, but the operator-facing live upload/progress UI is still Phase 02 work.
- The photoset POST path still finishes ingestion within the request lifecycle; the job record is truthful and reloadable, but frontend polling behavior is not implemented in this phase.

## Status
PASS

# Repo Repair Audit Phase 02

## Status

PASS

## Goal

Make `POST /api/v1/photosets` honestly asynchronous.

## Changes made

- updated [photosets.py](/opt/MediaCreator/apps/api/app/api/routes/photosets.py) so `POST /api/v1/photosets` now returns `202` after upload staging, pre-ingest photoset creation, and `photoset-ingest` job enqueue
- split [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py) into request-time queueing and worker-time ingest execution:
  - added `create_upload_staging_root()`
  - kept staged uploads available for the worker
  - added `execute_photoset_ingest_job(...)`
  - moved normalization, QC, classification, derivative writes, and manifest creation into the worker path
- updated [jobs.py](/opt/MediaCreator/apps/api/app/services/jobs.py) so `run_worker_once(...)` executes `photoset-ingest`
- updated [CharacterImportIngest.tsx](/opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx) so the operator sees truthful queued-ingest text while backend processing is still running
- added [photoset_test_utils.py](/opt/MediaCreator/apps/api/tests/photoset_test_utils.py) and migrated the affected API tests away from the old synchronous `201` photoset assumption
- updated [README.md](/opt/MediaCreator/README.md) and [PLANS.md](/opt/MediaCreator/PLANS.md) so the repo truth now matches the new async photoset route

## Pre-verification evidence

- [photosets.py](/opt/MediaCreator/apps/api/app/api/routes/photosets.py#L66) now declares `status_code=202`
- [jobs.py](/opt/MediaCreator/apps/api/app/services/jobs.py#L525) now has the real `validated_payload.kind == "photoset-ingest"` worker branch
- [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py#L1195) now exposes `execute_photoset_ingest_job(...)`
- the old `photoset_response.status_code == 201` assumption no longer appears in the API test suite

## Verification summary

- targeted async-ingest/API artifact proof passed:
  - `tests/test_photoset_job_progress.py`
  - `tests/test_photosets_intake_and_classification.py`
  - `tests/test_photosets_api.py`
  - `tests/test_photo_derivatives_and_manifests.py`
- truthful frontend queued-ingest UI proof passed:
  - `apps/web/tests/unit/CharacterImportIngest.test.tsx`
- broader migrated API sweep passed for the additional helper-converted tests
- `make lint`: passed
- `make typecheck`: passed

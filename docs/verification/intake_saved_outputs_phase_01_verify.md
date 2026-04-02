# Phase
`phase_01_backend_ingest_progress_and_person_first_routing`

## Scope verified
- required trimmed label validation
- duplicate-label acceptance
- bounded multi-file intake validation
- persisted per-entry bucket/reason reload stability
- ordered ingest job stage history and processed-count truth
- repo lint and typecheck after targeted backend proof

## Commands run
- `cd /opt/MediaCreator/apps/api && ../api/.venv/bin/pytest -q tests/test_photosets_intake_and_classification.py`
- `cd /opt/MediaCreator/apps/api && ../api/.venv/bin/pytest -q tests/test_photoset_job_progress.py`
- `make -C /opt/MediaCreator lint`
- `make -C /opt/MediaCreator typecheck`

## Artifact checks
- `POST /api/v1/photosets` rejected an empty/whitespace label with `400 Character label is required.`
- duplicate `character_label` uploads persisted as separate photosets
- reload check proved `GET /api/v1/photosets/{photoset_public_id}` returned stable bucket/reason data
- persisted bucket outcomes were observed in PostgreSQL for the first classified photoset:
  - `lora_only`
  - `body_only`
  - `both`
  - `rejected`
- `GET /api/v1/jobs/{job_public_id}` returned ordered stage history including:
  - `queued`
  - `upload_received`
  - `normalizing`
  - `person_check`
  - `qc_metrics`
  - `classification`
  - `derivative_write`
  - `complete`
  - `completed`
- completion gate proof asserted the ingest job was only completed after the expected `PhotosetEntry` rows existed

## UI checks
- none in this phase

## Results
- `tests/test_photosets_intake_and_classification.py`: `2 passed`
- `tests/test_photoset_job_progress.py`: `1 passed`
- `make -C /opt/MediaCreator lint`: passed
- `make -C /opt/MediaCreator typecheck`: passed
- body-only no-face intake stayed out of `rejected` and remained accepted for downstream use
- all four buckets were reproducibly produced and reloaded from persisted API state

## PASS/FAIL/BLOCKED decision
PASS

## Remaining risks
- Phase 01 does not yet add the operator-facing upload/progress UI; that remains Phase 02.
- Ingest is still request-bound, so the backend truth is persisted and queryable, but live frontend polling behavior is not yet exercised.

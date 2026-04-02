# Phase 01 verify — Backend ingest progress and person-first routing

## Verify goal

Prove that backend ingest is truthful, reloadable, and correctly routes person images into LoRA/body buckets.

## Mandatory verification order

1. read the paired build file
2. read the required experts
3. run the smallest targeted backend checks first
4. inspect persisted bucket/reason data
5. run broader lint/type checks only after targeted proof passes
6. update `docs/verification/intake_saved_outputs_phase_01_verify.md`

## Exact verification steps

### Verify step 1
Run API tests for label validation:
- empty label must fail
- duplicate label must succeed

### Verify step 2
Run API tests for multi-file upload validation and bounded ingest.

### Verify step 3
Run a job-progress test that proves ordered stage names and processed counts.

### Verify step 4
Run classification tests that prove all four buckets can be produced and reloaded.

### Verify step 5
Assert body-only no-face fixtures do not fall into `rejected` solely because face detection is false.

## Exact commands Codex should run

- `pytest -q tests/api/test_photosets_intake_and_classification.py`
- `pytest -q tests/api/test_photoset_job_progress.py`
- `make lint`
- `make typecheck`

If the repository uses different wrappers, Codex may map the commands to the repo’s existing test runner, but the verify report must list the exact real commands used.

## Deterministic pass conditions

Phase 01 is PASS only if:

- all targeted API tests pass
- job stage progression is real and ordered
- all four buckets are reproducibly testable
- the reload endpoint returns stable bucket/reason data
- the verify report includes exact commands and results

## Deterministic fail conditions

Phase 01 is FAIL if:

- any targeted API test fails
- duplicate labels are blocked
- body-only no-face inputs still fail due only to face absence
- job progress remains generic or non-persistent
- the verify report is incomplete

## Required verify report content

Write these sections into `docs/verification/intake_saved_outputs_phase_01_verify.md`:

- scope verified
- commands run
- test files executed
- bucket outcomes observed
- PASS/FAIL decision
- remaining risks
- exact blocker details if blocked

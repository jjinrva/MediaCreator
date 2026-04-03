# Phase 02 verify — true async photoset ingest and progress

## Required checks

- `POST /api/v1/photosets` returns `202`
- response includes a real `job_public_id`
- ingest job is not already falsely completed on initial response
- worker executes `photoset-ingest`
- `/api/v1/jobs/{job_public_id}` shows progress through ingest stages
- final photoset detail shows persisted entries and artifacts
- tests no longer depend on `photoset_response.status_code == 201`

## Mandatory evidence

- API integration test output
- worker execution proof
- artifact/manifests existence proof
- verification report

## Fail if

- the route still performs ingest inline
- the worker still lacks a `photoset-ingest` branch
- a job can complete without entries/manifests

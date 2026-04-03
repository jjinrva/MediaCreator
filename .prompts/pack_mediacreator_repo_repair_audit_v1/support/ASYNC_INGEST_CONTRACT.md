# Async ingest contract

This pack must make photoset ingest honestly asynchronous.

## Required backend behavior

### POST /api/v1/photosets
Must:
- stage the uploaded files to a safe temporary area
- create a photoset record in a pre-ingest status
- enqueue a `photoset-ingest` job
- return `202 Accepted`
- return at least:
  - `photoset_public_id`
  - `job_public_id`
  - initial status / counts
- must not execute QC/classification/derivative generation inline after the files are staged

### Worker
Must:
- contain an explicit `photoset-ingest` execution branch
- claim the queued ingest job
- run the existing normalization / person-check / QC / classification / derivative pipeline
- advance job progress stages and counts while executing
- mark the photoset/job failed on errors
- never mark the ingest job completed without persisted entries and manifests

## Required frontend behavior

The UI must show two distinct truths:

1. browser transfer progress
2. backend ingest progress after transfer completes

The UI may not imply that server-side processing is happening live if the request has not yet returned a `job_public_id`.

## Required verification

- API returns `202`
- response includes a job reference
- worker execution produces entries and manifests
- polling `/api/v1/jobs/{job_public_id}` shows progressing stage/counts
- final photoset detail resolves correct entries, buckets, and artifact URLs

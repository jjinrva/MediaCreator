# Phase 02 build — true async photoset ingest and progress

## Goal

Make `POST /api/v1/photosets` honestly asynchronous.

## Required design

### Request-time responsibilities
- accept multipart upload
- stage files safely
- create a pre-ingest photoset record
- enqueue `photoset-ingest`
- return `202` with:
  - `photoset_public_id`
  - `job_public_id`
  - initial counts/status

### Worker-time responsibilities
- claim `photoset-ingest`
- run the real normalization/QC/classification/derivative pipeline
- advance stage history and counts
- create entries/manifests
- fail honestly on errors

## Required code changes

1. Split current inline ingest
   - keep reusable ingest logic
   - extract the work portion into a worker-executable function

2. Add a real worker branch
   - `apps/api/app/services/jobs.py` must handle `validated_payload.kind == "photoset-ingest"`

3. Update the route contract
   - `apps/api/app/api/routes/photosets.py` must return `202`, not `201`

4. Update the tests
   - remove synchronous-completion assumptions
   - update tests that expect `photoset_response.status_code == 201`
   - add tests that poll the ingest job and then verify the final photoset

5. Keep the existing frontend polling model, but make it truthful
   - do not fake server-side progress before a real job exists

## Required safety checks

- staged files cleaned up only after the worker no longer needs them
- failed ingest does not leave the photoset falsely marked prepared
- completed ingest cannot occur without entries and manifests

## Do not do in this phase

- do not recalibrate QC thresholds yet
- do not change 3D/proof generation yet

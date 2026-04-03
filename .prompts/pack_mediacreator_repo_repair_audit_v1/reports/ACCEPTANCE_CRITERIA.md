# Acceptance criteria

## Repo truth
- `PLANS.md` no longer marks unimplemented or partial capabilities as full PASS
- `README.md` no longer claims immediate-return/202 behavior for routes that do not do that
- no screen or payload implies refined 3D or proof-image output unless the artifact exists

## Intake
- `POST /api/v1/photosets` returns `202`
- response contains a valid `job_public_id`
- queued ingest is later executed by the worker
- UI shows browser transfer progress and backend ingest progress as separate states

## QC / routing
- image with no person is rejected
- image with strong face evidence but weak body evidence can be `lora_only`
- image with strong body evidence but no face can be `body_only`
- image with both strong face and body evidence can be `both`
- rejection reasons are explicit and stable
- body-only images are not rejected solely for missing face evidence

## Saved character / 3D
- accepted photos can create a saved character record
- preview/base GLB exists and resolves through the API when the preview job completes
- 3D status explicitly distinguishes proxy/base GLB from refined mesh
- the app never labels proxy/base output as refined 3D

## LoRA / proof image
- when AI Toolkit or generation runtime is unavailable, the UI/API show `BLOCKED`-style truth and do not claim proof output
- when capability is ready, proof-image generation creates a real file and corresponding storage record
- a saved generation request alone does not count as a proof image

## Verification
- deterministic API tests cover the repaired contracts
- artifact existence is checked directly
- no phase passes without a verify report

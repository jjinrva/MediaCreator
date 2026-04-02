# MediaCreator audit report — static code audit

## Audit basis

This audit is based on the checked-in code in the uploaded `MediaCreator-slim-20260402-171149.zip` snapshot.

Key evidence files inspected:
- `scripts/run-api.sh`
- `scripts/run-web.sh`
- `.env.example`
- `apps/api/app/main.py`
- `apps/web/next.config.mjs`
- `apps/web/components/character-import/CharacterImportIngest.tsx`
- `apps/api/app/api/routes/photosets.py`
- `apps/api/app/services/photo_prep.py`
- `apps/api/app/services/characters.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/api/routes/exports.py`
- `apps/api/app/api/routes/lora.py`
- `apps/api/app/api/routes/video.py`
- `apps/web/components/glb-preview/GlbPreview.tsx`
- `apps/web/components/reconstruction-status/ReconstructionStatus.tsx`
- `apps/web/components/lora-training-status/LoraTrainingStatus.tsx`
- `apps/web/app/studio/characters/[publicId]/page.tsx`

## Executive summary

The repo is **not empty** and several major pieces are genuinely implemented:
- photo upload and QC exist
- base character creation exists
- numeric body, pose, and face parameter persistence exist
- a jobs table and a worker loop exist
- Blender export, reconstruction, LoRA, motion, video, and generation surfaces exist

However, the current runtime has four structural problems that make it feel broken:

1. **The user cannot see real long-running progress**
   - There is no general progress UI or polling path on the character flow.
   - The UI does not expose job state in a clear way after upload or during generation.

2. **Long-running routes are not truly backgrounded**
   - `POST /api/v1/exports/.../preview`
   - `POST /api/v1/exports/.../reconstruction`
   - `POST /api/v1/lora/...`
   - `POST /api/v1/video/.../render`
   all queue work and then immediately call `run_worker_once()` inline in the request handler.
   This defeats the worker model and makes progress impossible to monitor honestly.

3. **The ingest workflow is truthful about QC, but not truthful about acceptance**
   - `create_character_from_photoset()` currently uses **all** `photoset_entries`.
   - Failed QC images are not filtered out before character creation.
   - The upload page does not show accepted/rejected counts or gate creation strongly enough.

4. **The runtime is still tied to one machine IP in many places**
   - `10.0.0.102` is hardcoded in runtime defaults, tests, docs, and web fallbacks.
   - API CORS allows only one browser origin by default.
   - This is fragile on a headless LAN machine.

## What is already implemented and usable

### Implemented
- API bind host default is `0.0.0.0` in `scripts/run-api.sh`
- web bind host default is `0.0.0.0` in `scripts/run-web.sh`
- photoset upload with `UploadFile` exists
- photo QC and derivative generation exist
- base character creation from photoset exists
- body parameter save path exists
- pose parameter save path exists
- face parameter save path exists
- jobs table and worker loop exist
- preview export route exists
- reconstruction route exists
- LoRA training route exists
- video render route exists
- character detail screen exists

### Partially implemented
- job orchestration
- visible progress
- worker status visibility
- LAN-safe runtime defaults
- accepted-photo gating
- generation-path usability after ingest

## Findings

### Finding 1 — bind hosts are fine, public/origin defaults are not
**Severity:** High

Good:
- `scripts/run-api.sh` uses `MEDIACREATOR_API_HOST:-0.0.0.0`
- `scripts/run-web.sh` uses `MEDIACREATOR_WEB_HOST:-0.0.0.0`

Broken:
- `.env.example` defaults `MEDIACREATOR_WEB_PUBLIC_HOST`, `MEDIACREATOR_API_PUBLIC_HOST`, and `NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL` to `10.0.0.102`
- `apps/api/app/main.py` sets CORS from one fixed origin based on `MEDIACREATOR_WEB_PUBLIC_HOST`
- `apps/web/next.config.mjs` hardcodes `allowedDevOrigins: ["10.0.0.102"]`
- nearly every client component falls back to `http://10.0.0.102:8010`

Impact:
- the app is not portable across LAN IP changes
- browser/API origin drift is likely on a headless machine
- docs and tests reinforce the wrong contract

### Finding 2 — long-running routes are synchronous in practice
**Severity:** Critical

Routes inspected:
- `apps/api/app/api/routes/exports.py`
- `apps/api/app/api/routes/lora.py`
- `apps/api/app/api/routes/video.py`

Problem:
- these routes enqueue a job and then immediately call `run_worker_once()`
- the HTTP request blocks until the job completes or fails
- the worker process is bypassed for these user-facing flows
- there is no honest progress opportunity for the user

Impact:
- “it might be working in the background” is impossible to answer from the UI
- if Blender/AI Toolkit/video work is slow, the request simply hangs
- queued/running states are effectively hidden from the user

### Finding 3 — the worker exists, but there is no heartbeat or liveness surface
**Severity:** High

Evidence:
- `apps/worker/src/mediacreator_worker/main.py` loops and runs `run_worker_once()`
- there is no heartbeat table or worker-liveness API signal
- `/api/v1/system/status` reports generation/blender/AI Toolkit/storage, but not worker health

Impact:
- a queued job can sit forever if the worker is not running
- the operator has no first-class “worker stale/offline” message

### Finding 4 — upload/QC are synchronous and real, but the next-step UX is weak
**Severity:** High

Evidence:
- `CharacterImportIngest.tsx` uploads to `/api/v1/photosets`
- after upload, the page shows persisted entries and a `Create base character` button
- there is no accepted/rejected summary
- there is no “you are now at step 2 of 3” status
- there is no automatic preview queue after base character creation

Impact:
- users can easily think upload should have started full generation
- the actual next step is present but not strong enough

### Finding 5 — character creation does not filter out QC-failed photos
**Severity:** Critical

Evidence:
- `apps/api/app/services/characters.py`
- `photoset_entries = session.scalars(...).all()`
- all entries are used to create the character
- there is no `qc_status` filter before accepted entry ids are stored

Impact:
- failed QC entries become part of the base character record
- this undermines later 3D/LoRA quality

### Finding 6 — there is no reusable job-progress component in the web app
**Severity:** High

Evidence:
- no general component polls `/api/v1/jobs/{job_public_id}`
- no screen displays `progress_percent` + `step_name` as a live progress view
- `GlbPreview`, `ReconstructionStatus`, `LoraTrainingStatus`, and `VideoRenderPanel` simply wait for the action to return

Impact:
- the user cannot tell queued vs running vs failed until the request ends
- failures are less diagnosable than they should be

### Finding 7 — the character detail page does not foreground generation status
**Severity:** Medium

Evidence:
- detail page shows body/pose/face/history/outputs
- outputs show status snapshots, but not a real live progress panel
- `StudioFrame` current path is set to `/studio/characters/new` inside the detail page, which is wrong for route context

Impact:
- status is present, but not actionable
- navigation context is slightly incorrect

### Finding 8 — upload handling reads every file fully into memory and lacks hard limits
**Severity:** Medium

Evidence:
- `create_photoset()` loops through uploads and does `await upload.read()`
- there is no explicit count limit or per-file size validation before ingest

Impact:
- a large photoset can consume too much memory
- failure behavior is less controlled than it should be

## Exact remediation decision

This pack fixes the runtime with one chosen path:

1. keep bind hosts on `0.0.0.0`
2. remove hardcoded `10.0.0.102` from runtime defaults
3. keep upload/QC synchronous so QC results return immediately
4. treat `pass` and `warn` as accepted; treat `fail` as rejected
5. block character creation when accepted count is zero
6. keep the existing jobs table and worker process
7. stop calling `run_worker_once()` inside request handlers
8. return `202 Accepted` with job metadata for long-running routes
9. add worker heartbeat storage and UI surfacing
10. add one reusable job-progress card that polls `/api/v1/jobs/{job_public_id}`
11. after base character creation, immediately queue preview export and redirect to the detail page so the user sees progress

## Expected end state after this repair pack

- upload still returns QC results immediately
- the upload page clearly shows accepted/rejected counts
- failed QC images are excluded from character creation
- base character creation is obvious and truthful
- preview export is queued, not executed inline
- character detail shows live progress for preview generation
- worker health is visible
- the app works from any LAN address without fixed-IP assumptions

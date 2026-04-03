# MediaCreator repo audit — 2026-04-03

## Audit basis

This audit is based on the uploaded repo snapshot extracted from:

- `MediaCreator-review-slim-20260402-235253.zip`
- embedded snapshot identifier: `4c95e6c06107c90f35b802b1292b0e200157db26`

Primary files inspected:

- `PLANS.md`
- `README.md`
- `apps/api/app/api/routes/photosets.py`
- `apps/api/app/services/photo_prep.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/services/reconstruction.py`
- `apps/api/app/services/exports.py`
- `apps/api/app/services/prompt_expansion.py`
- `apps/api/app/services/lora_training.py`
- `apps/web/components/character-import/CharacterImportIngest.tsx`
- `scripts/blender/rigify_proxy_export.py`
- selected API tests, especially:
  - `apps/api/tests/test_photoset_job_progress.py`
  - `apps/api/tests/test_saved_3d_output_contract.py`
  - `apps/api/tests/test_lora_proof_image_contract.py`

## Executive summary

The repo contains a substantial amount of truthful scaffolding, but the declared project status is materially ahead of the actual implementation.

The strongest current capabilities are:

- labeled photoset intake
- QC classification into usable buckets
- persisted derivatives and manifests
- saved character records
- queued Blender preview export
- conditional LoRA training registry flow

The biggest gaps are:

1. **ingest is still synchronous**
2. **worker does not actually execute `photoset-ingest` jobs**
3. **status/docs claim more completion than the code supports**
4. **3D output is a rigged proxy/base GLB, not a photo-derived refined character mesh**
5. **generation requests are stored, but proof-image generation is not implemented end-to-end**

## Where the code should be vs where it actually is

| Area | Where it should be by this point | What the snapshot actually does | Gap severity |
|---|---|---|---|
| Project status truth | Phases marked PASS only when fully implemented and verified | `PLANS.md` marks all 26 phases PASS | Critical |
| Intake API | `POST /api/v1/photosets` should return quickly and hand ingest to the worker | Route returns `201` and runs `ingest_photoset(...)` inline inside the request | Critical |
| Worker coverage | Worker should execute all queued long-running job kinds used by product flow | `run_worker_once(...)` handles preview export, reconstruction, LoRA, video — but not `photoset-ingest` and not generation/proof-image jobs | Critical |
| Upload progress truth | Browser upload progress and backend ingest progress should both be real | Frontend is built for dual progress, but backend ingest happens before response completes | Critical |
| QC routing | First decide “person present?”, then LoRA/body suitability, with clear fallback for body-only images | Current QC mostly does this, but thresholds and detection fallbacks likely over-reject valid images in practice | High |
| Character label | Required, duplicate allowed | This is already implemented | Keep |
| Thumbnail enlarge | Clicking a thumbnail should enlarge it | This is already implemented | Keep |
| Body preprocessing | Body-qualified images should produce a background-removed derivative | This is already implemented via `rembg` | Keep |
| LoRA preprocessing | LoRA-qualified images should receive conservative normalization only | This is already implemented | Keep |
| Saved 3D output | A saved character should have a truthful 3D stage and, by roadmap claim, be more than a proxy scaffold | Current output is a Blender-generated proxy/base GLB plus optional detail-prep manifest; no refined mesh is generated | High |
| Reconstruction truth | Detail-prep should not be confused with refined reconstruction | Current code is truthful internally, but global docs/status overstate phase completion | High |
| LoRA training | Real local training should run only when runtime is actually ready | Current code is conditional on AI Toolkit + NAS and is honest about that | Medium |
| Proof image generation | There should be an actual queued generation job and saved proof image when capability is ready | Current code stores a generation-request asset only; no proof-image job/artifact path exists | Critical |

## Concrete findings

### 1. All 26 phases are marked PASS, but the code is not at that end-state

- `PLANS.md:7-34` marks phases 01 through 26 as `PASS`.
- That conflicts with the current code state below.

### 2. README says photoset upload/QC return immediately and long-running POSTs return `202`, but the route still runs intake inline

- `README.md:80-84` says photoset upload and QC return immediately and job progress comes from `GET /api/v1/jobs/...`
- `README.md:180-184` says long-running POST routes return `202 Accepted`
- But `apps/api/app/api/routes/photosets.py:67-104` declares `status_code=201` and directly calls `ingest_photoset(...)` inside the request transaction.

### 3. The frontend already expects async ingest progress, but the backend cannot provide real server-side progress during the request

- `apps/web/components/character-import/CharacterImportIngest.tsx:499-576` polls `/api/v1/jobs/{job_public_id}`
- `CharacterImportIngest.tsx:706-713` switches the UI to a `server` phase after browser upload completes
- `CharacterImportIngest.tsx:897-958` shows server stage and processed-file counts
- Because the API does ingest inline, the browser does not get real live backend progression during the request itself.

### 4. The ingest job model exists, but ingest is not actually delegated to the worker

- `apps/api/app/services/photo_prep.py:699-718` enqueues a `photoset-ingest` job and immediately starts it
- `photo_prep.py:732-1110` then performs the ingest work inline and completes the job before the API responds
- `apps/api/app/services/jobs.py:47-54` defines `PhotosetIngestJobPayload`
- But `jobs.py:492-650` does not contain a `validated_payload.kind == "photoset-ingest"` execution branch
- If a `photoset-ingest` job were ever claimed by the worker, it would fall through to `complete_job(...)` at `jobs.py:649-650` without doing ingest work

### 5. Several requested intake rules are already implemented and should be preserved

- character label required:
  - `photo_prep.py:426-432`
  - `CharacterImportIngest.tsx:843-858`
- duplicate labels allowed:
  - `CharacterImportIngest.tsx:856-858`
- thumbnail click-to-enlarge:
  - `CharacterImportIngest.tsx:999-1077`
- body-only images with no face can still route to body modeling:
  - LoRA requires face at `photo_prep.py:553-556`
  - body modeling requires body evidence at `photo_prep.py:558-561`
- no-person rejection happens first:
  - `photo_prep.py:527-538`
- body background removal exists:
  - `photo_prep.py:274-287`
- conservative LoRA normalization exists:
  - `photo_prep.py:290-313`

### 6. The current 3D output is a proxy/base rigged GLB, not a refined photo-derived character mesh

- `scripts/blender/rigify_proxy_export.py:60-175` builds the mesh from cubes, spheres, and cylinders
- `reconstruction.py:220-253` writes a `detail-prep-manifest`
- `reconstruction.py:233-236` explicitly records `refined_detail_mesh_generated: False`
- `exports.py:187-192` explicitly states that Phase 18 does not claim a freeform refined mesh yet

### 7. Proof-image generation is not implemented end-to-end

- `prompt_expansion.py:526-567` creates a `generation-request` asset and stores metadata
- `jobs.py:47-110` contains no generation/proof-image job payload type
- `test_lora_proof_image_contract.py:89-119` confirms that when runtime generation is unavailable, the app stores a request but no proof image storage object is created
- There is no corresponding execute-generation worker path in `jobs.py`

### 8. Existing tests reinforce the synchronous-intake contract, so an honest fix will require broad test updates

- `test_photoset_job_progress.py:201-245` expects `POST /api/v1/photosets` to return `201` and the ingest job to already be completed
- Many other API tests expect `photoset_response.status_code == 201`

## What I would change first

### P0 — must fix now
1. Make photoset ingest truly asynchronous:
   - split request-time upload staging from worker-time ingest execution
   - return `202` with `job_public_id`
   - implement a real `photoset-ingest` worker branch
2. Reset truth:
   - stop claiming all phases PASS
   - stop implying end-to-end outputs exist where only scaffolds exist
3. Add a real generation job type and saved proof-image path, or explicitly block proof-image claims until that exists

### P1 — next
4. Calibrate QC acceptance and add fallback logic/logging for valid body shots
5. Make 3D status explicit:
   - `proxy_glb_available`
   - `detail_prep_available`
   - `refined_mesh_available`
6. Add deterministic end-to-end acceptance tests for intake → character → preview GLB → dataset → LoRA/proof output

### P2 — after that
7. Improve UI text around upload/server stages
8. Expose reason-code detail and confidence detail to help explain rejections
9. Auto-queue preview export only when accepted inputs are present and artifact lineage checks pass

## Already correct enough to keep

Do not rewrite these from scratch:

- required character label with duplicate labels allowed
- thumbnail click-to-enlarge behavior
- person-first QC structure
- background removal for body derivatives
- conservative lighting/color normalization for LoRA derivatives
- truthful conditional LoRA readiness checks

## Bottom line

The repo is **not** actually at “all phases PASS.”

It is closer to:

- **intake/QC:** moderately real
- **saved character persistence:** real
- **preview GLB/base 3D:** real but proxy/base-level
- **detail reconstruction:** scaffold contract only
- **LoRA training:** conditionally real
- **LoRA proof-image generation:** not implemented end-to-end
- **global truthfulness/status reporting:** inconsistent

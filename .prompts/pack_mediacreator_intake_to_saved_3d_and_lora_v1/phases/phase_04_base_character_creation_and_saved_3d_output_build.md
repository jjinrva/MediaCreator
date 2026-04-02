# Phase 04 build — Base character creation and saved 3D output

## Phase goal

Create a saved character from accepted assets only and produce a truthful saved 3D output path.

## Experts Codex must use for this phase

- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

## Exact chosen path

- Create the base character from accepted assets only.
- Use the photoset label as the default human-facing character label.
- Allow duplicate labels.
- Create a saved character even if only one body-qualified input exists.
- If there are three or more body-qualified images, also queue the higher-detail body path; if there are fewer than three, still produce the saved base 3D output and mark refinement unavailable or skipped truthfully.
- Queue the 3D work through the existing job system.
- The detail page must show real progress and a real GLB when ready.

## Exact stack and libraries

- FastAPI
- SQLAlchemy
- existing jobs table and worker
- Blender runtime / current reconstruction service
- existing `<model-viewer>` GLB viewer

### Source IDs for this phase
S04, S05, S06, S07, S12

## Exact file areas

Start with these files:

- `apps/api/app/services/characters.py`
- `apps/api/app/api/routes/characters.py`
- `apps/api/app/api/routes/exports.py`
- `apps/api/app/services/reconstruction.py`
- `apps/api/app/services/blender_runtime.py`
- `apps/web/app/studio/characters/[publicId]/page.tsx`
- `apps/web/components/glb-preview/GlbPreview.tsx`

## Ordered steps

### Step 1 — create saved character from accepted sources only

Character creation must:
- require at least one accepted source asset overall
- link accepted source assets by bucket
- reject creation when all images are rejected
- allow duplicate human-facing labels
- store history and lineage

**Verification immediately after Step 1**
- add API tests for:
  - zero accepted assets => fail
  - duplicate label => success
  - accepted source asset linkage => persisted

### Step 2 — queue saved 3D output work

On character creation or the first explicit 3D-create action:
- queue the base 3D job
- if body-qualified count >= 3, queue refinement as a later step or nested output
- if body-qualified count < 3, do not fake refinement readiness

Do not run long 3D work inline in the request handler.

**Verification immediately after Step 2**
- add tests that the route returns queued job metadata, not inline-computed fake completion
- assert the job/output record exists after queueing

### Step 3 — truthful detail page status and full-body preview

The detail page must show:
- current 3D job state
- clear queued/running/failed/complete labels
- full-body framing in the viewer
- artifact-backed GLB only when the file exists

Do not mark complete on status alone. Check the artifact path.

**Verification immediately after Step 3**
- add Playwright coverage for status visibility and full-body preview section
- add a backend artifact existence check used by the UI/API

### Step 4 — save the 3D artifact and record it

When the job completes:
- write the GLB artifact
- register the output row
- write the history event
- expose the saved output on reload

**Verification immediately after Step 4**
- add a file-existence assertion test
- add a reload test for the detail page

## Pass/fail criteria

### PASS
- character creation uses accepted assets only
- duplicate labels are allowed
- a saved GLB path is produced through the job system
- full-body preview is available from a real artifact
- refinement availability is truthful when capture is limited

### FAIL
- rejected assets leak into the character record
- duplicate labels are blocked
- 3D work still runs inline in the request
- the UI says complete before the GLB exists
- reload loses the saved output

## Deliverables

- saved character creation patch
- saved 3D output queueing path
- character detail progress patch
- artifact existence checks
- targeted API/UI/output tests

## Forbidden scope

- do not add wardrobe or motion controls
- do not switch to a new 3D framework
- do not fake refinement outputs when input count is insufficient

## Documentation Codex must update in this phase

- `docs/phase_reports/intake_saved_outputs_phase_04.md`
- `docs/verification/intake_saved_outputs_phase_04_verify.md`

## Exit condition

The phase may stop only when a saved GLB path is testable and the paired verify file can prove the UI does not overstate completion.

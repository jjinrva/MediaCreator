# Phase 16 build — Face/expression parameter foundation

## Goal

Lay the numeric groundwork for later facial controls by defining expression parameters and a minimal face-control surface.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- MediaPipe Face Landmarker
- Blender ShapeKey-compatible controls
- Radix Slider

### Source IDs to use for this phase
S21, S29, S19



## Files and directories this phase is allowed to create or modify first

- apps/api/app/models/facial_parameters.py
- apps/web/components/face-editor

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Define the facial parameter catalog as a numeric system just like the body and pose catalogs. Start with a minimal but useful set: jaw open, smile left/right, brow raise, eye openness, and neutral expression blend factor.

### Step 2
Document how these parameters will later map to Blender facial shape keys or corrective rigs. The first implementation can be a scaffolded control surface with persisted values even if the full facial deformation is refined later.

### Step 3
Add the face editor section to the character detail page only if it is truthful. If the UI is added in this phase, it must persist values and write history just like body and pose.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_16.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- facial parameter contract
- optional minimal face editor
- docs for future face-to-rig mapping

## What Codex must not do in this phase


- Do not create parallel implementations of the same concept.
- Do not add auth or multi-user logic in this phase unless the phase explicitly says to create future-ready fields only.
- Do not seed runtime screens with demo/sample data.
- Do not change the chosen stack.
- Do not continue to the next phase until this phase passes verify.


## Exit condition for the build phase

The build phase may stop only when:
1. the phase deliverables exist,
2. the changed code is coherent,
3. the paired verify file has enough hooks to test the phase honestly,
4. `docs/phase_reports/phase_16.md` is updated with exact commands and results.

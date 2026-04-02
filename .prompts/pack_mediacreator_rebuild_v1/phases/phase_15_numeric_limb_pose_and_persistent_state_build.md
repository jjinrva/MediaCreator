# Phase 15 build — Numeric limb posing and persistent pose state

## Goal

Add arm and leg controls as numeric pose parameters that persist, map to the rig later, and survive reloads now.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Radix Slider
- FastAPI
- Blender PoseBone-compatible naming

### Source IDs to use for this phase
S05, S06, S08, S10, S30, S31



## Files and directories this phase is allowed to create or modify first

- apps/web/components/pose-editor
- apps/api/app/models/pose_state.py
- apps/api/app/api/routes/pose.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Define the canonical pose state model as bone-axis numeric values, not as free-form descriptive text. Phase 15 covers left arm, right arm, left leg, and right leg only. Each control must have explicit min, max, step, and unit.

### Step 2
Build the pose editor UI using the same shared slider and tooltip pattern as the body editor. Persist on `onValueCommit`. Show the numeric values clearly so they can later map to natural-language phrases like 'raise left arm by 15 degrees'.

### Step 3
Store pose state independently from body state but link it to the current character asset. Write history on every committed pose change. The detail page must rehydrate the pose state from the API on reload.

### Step 4
Trigger the GLB preview refresh after a pose commit so the preview remains aligned with the saved state.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_15.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- pose state model
- pose editor UI
- pose update API
- preview refresh on save

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
4. `docs/phase_reports/phase_15.md` is updated with exact commands and results.

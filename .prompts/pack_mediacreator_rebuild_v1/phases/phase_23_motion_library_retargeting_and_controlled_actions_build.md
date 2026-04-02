# Phase 23 build — Motion/action library, retargeting, and controlled animation inputs

## Goal

Make MediaCreator control rigged characters with reusable action clips instead of relying on AI video generation to fake motion.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/MOTION_AND_VIDEO_EXPERT.md`
- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Blender actions
- Rigify-compatible rigs
- optional Mixamo import support

### Source IDs to use for this phase
S27, S28, S30, S43



## Files and directories this phase is allowed to create or modify first

- apps/api/app/services/motion_library.py
- apps/web/app/studio/motion
- docs/architecture/motion_contract.md

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create the motion asset model now. A motion clip needs a name, duration, source, compatible rig class, and action file or action payload reference. The app must treat motion as a reusable asset, not just a text instruction.

### Step 2
Seed a small local motion library by generating or importing real actions for: idle, walk, jump, sit, turn. These must be rig-driven. If external imports are used, store them locally and register their source.

### Step 3
Support optional import of external humanoid animations later, with Mixamo documented as a recommended source. Do not make Adobe login a hard dependency for the app to function.

### Step 4
Create a minimal motion screen where the user can choose a character and preview an action assignment.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_23.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- motion asset model
- seed action library
- motion screen
- motion contract doc

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
4. `docs/phase_reports/phase_23.md` is updated with exact commands and results.

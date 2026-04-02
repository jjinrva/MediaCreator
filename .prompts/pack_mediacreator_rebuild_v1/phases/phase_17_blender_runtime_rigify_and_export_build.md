# Phase 17 build — Blender runtime, Rigify rig generation, and model attachment

## Goal

Make Blender the authoritative runtime for rig creation, numeric parameter application, GLB export, and character attachment.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Blender 4.5 LTS
- Rigify
- glTF exporter
- Python subprocess/job execution

### Source IDs to use for this phase
S25, S26, S27, S28, S29, S30


## Exact chosen path for this phase

- Blender 4.5 LTS is the canonical DCC/runtime.
- Rigify is the baseline rig generation path.
- Export format is GLB via the official Blender glTF exporter.
- Numeric body values are designed to map to Blender shape keys.
- Numeric pose values are designed to map to Blender pose bones.


## Files and directories this phase is allowed to create or modify first

- workflows/blender
- scripts/blender
- apps/api/app/services/blender_runtime.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create a Blender runtime service that can invoke Blender in background mode with a versioned Python script and a clear job payload. The payload must include the character public ID, input asset paths, numeric body values, numeric pose values, and output target paths.

### Step 2
Use Rigify as the rig-generation baseline. The app does not need to expose Rigify to the user; it needs to produce a rigged character pipeline that is stable and scriptable.

### Step 3
Define a Blender-side data contract for applying numeric body parameters and numeric pose parameters. Even if some values initially map to coarse deformations, the mapping must be explicit and documented.

### Step 4
Create a GLB export step using Blender’s glTF exporter. Export textures, normals, tangents, skins, animations if present, and morph targets if present.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_17.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- Blender runtime service
- Rigify baseline pipeline
- GLB export job

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
4. `docs/phase_reports/phase_17.md` is updated with exact commands and results.

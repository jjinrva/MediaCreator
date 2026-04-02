# Phase 19 build — Skin, color, texture, and material fidelity path

## Goal

Improve realistic color, skin texture, and material representation so the character model is useful beyond a flat geometry pass.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/WARDROBE_AND_MATERIALS_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Blender materials
- texture projection
- glTF texture export
- prepared capture derivatives

### Source IDs to use for this phase
S28, S29, S31, S23, S24



## Files and directories this phase is allowed to create or modify first

- apps/api/app/services/texture_pipeline.py
- docs/architecture/texture_material_fidelity.md

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create a texture/material pipeline that starts from prepared photos and projects or synthesizes texture outputs suitable for the rigged character. The first success criterion is truthful full-color textured output, not a perfect cinema-grade skin shader.

### Step 2
Persist texture artifacts separately from geometry artifacts. A character should be able to have a base mesh, a refined mesh, a base texture set, and a refined texture set. This becomes important later for wardrobe and rendering workflows.

### Step 3
Make the export path carry textures into GLB outputs where the exporter and preview support it. Later phases can add higher-end export packages if needed.

### Step 4
Document what is 'base color only' versus 'high-detail texture' so the UI and exported outputs are honest.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_19.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- texture pipeline service
- texture/material fidelity doc
- textured output metadata

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
4. `docs/phase_reports/phase_19.md` is updated with exact commands and results.

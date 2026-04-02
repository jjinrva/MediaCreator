# Phase 18 build — High-detail 3D reconstruction/refinement path

## Goal

Add the best practical automatic path toward high-detail, full-color, textured human 3D models while keeping the app riggable and controllable.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/DIFFUSION_COMFYUI_AND_LORA_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- SMPL-X/SMPLify-X/SMPLest-X ecosystem
- COLMAP
- Blender

### Source IDs to use for this phase
S32, S33, S34, S35, S36, S25, S28


## Exact chosen path for this phase

- First create a riggable parametric body fit with the SMPL-X ecosystem.
- Then add a detail-refinement layer informed by higher-quality multi-view capture and COLMAP-backed reconstruction/material projection.
- Do not replace the riggable base with an uncontrolled detail mesh.


## Files and directories this phase is allowed to create or modify first

- docs/architecture/high_detail_3d_path.md
- apps/api/app/services/reconstruction.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Use a two-stage path. Stage 1: fit a riggable parametric human model using the SMPL-X family. Stage 2: refine geometric and appearance detail from multi-view capture using COLMAP-backed reconstruction and texture projection where capture quality allows it.

### Step 2
Do not let a detail-reconstruction method replace the riggable base mesh. The whole point of the app is that the user can pose and control the character later. The detail layer must support, not replace, that requirement.

### Step 3
Create the reconstruction service contract now. It should accept a capture set, choose the current reconstruction strategy, and write outputs/history/job records. The first implementation can truthfully support only the riggable base and a partial detail pass if full refinement is not yet finished, but the architecture must be exact.

### Step 4
Document the capture requirements for the high-detail path, especially the need for more images, overlap, and stable lighting if the user wants research-grade fidelity.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_18.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- high-detail 3D strategy doc
- reconstruction service contract
- job/output model for refinement

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
4. `docs/phase_reports/phase_18.md` is updated with exact commands and results.

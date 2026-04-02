# Phase 22 build — Wardrobe ingestion from photo, AI wardrobe generation, and closet catalog

## Goal

Create reusable wardrobe assets from user photos or AI text prompts, preserve materials and color metadata, and expose a closet catalog UI.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/WARDROBE_AND_MATERIALS_EXPERT.md`
- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/DIFFUSION_COMFYUI_AND_LORA_EXPERT.md`
- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- ComfyUI
- Blender
- asset registry
- closet catalog UI

### Source IDs to use for this phase
S37, S38, S39, S28, S31



## Files and directories this phase is allowed to create or modify first

- apps/web/app/studio/wardrobe
- apps/api/app/services/wardrobe.py
- apps/api/app/api/routes/wardrobe.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create the wardrobe asset model. Separate the base garment asset from fitting data, color variants, and material variants. A closet item is not just one prompt string; it is a reusable asset with its own metadata and lineage.

### Step 2
Implement two wardrobe creation paths. Path A: single-photo garment ingest, which stores the photo, derives or generates a garment representation, and asks for garment type/material metadata where needed. Path B: AI garment generation from prompt text like 'black tank top'.

### Step 3
Store explicit material and color metadata now. Later phases can deepen the simulation, but the data model must already know whether an item is cotton, leather, satin, denim, etc., and what its base color is.

### Step 4
Create a closet catalog screen that lists real wardrobe items only. No sample/demo outfits.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_22.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- wardrobe asset model
- closet catalog
- photo path
- AI path
- material/color metadata

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
4. `docs/phase_reports/phase_22.md` is updated with exact commands and results.

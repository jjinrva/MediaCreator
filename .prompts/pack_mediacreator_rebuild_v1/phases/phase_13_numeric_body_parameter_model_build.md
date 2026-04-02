# Phase 13 build — Numeric body parameter model and backend contracts

## Goal

Define the body-parameter system as explicit numeric fields that can later map to natural-language edits and Blender shape keys.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- SQLAlchemy
- Pydantic
- Blender ShapeKey-compatible parameter design

### Source IDs to use for this phase
S29, S11, S12, S19



## Files and directories this phase is allowed to create or modify first

- apps/api/app/models/body_parameters.py
- apps/api/app/schemas/body_parameters.py
- docs/architecture/body_parameter_contract.md

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create the canonical body parameter schema now. Each parameter must have a stable key, display label, min, max, step, unit, default value, and grouping metadata. Store values numerically. Do not store natural-language phrases as the canonical truth.

### Step 2
Use a parameter naming contract that can later map to Blender shape keys and learned language mappings. Examples include torso scale, shoulder width, chest volume, waist width, hip width, thigh volume, calf volume, and arm volume.

### Step 3
Document the exact parameter contract in `docs/architecture/body_parameter_contract.md`. This document is critical because later phases will map these values into Blender and eventually into natural-language intent.

### Step 4
Create a read API that returns the parameter catalog and the current character values.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_13.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- body parameter schema
- catalog API
- body parameter architecture doc

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
4. `docs/phase_reports/phase_13.md` is updated with exact commands and results.

# Phase 11 build — Character asset registry, history, and base-character creation

## Goal

Turn an accepted photoset into a real base character record with asset lineage, a public ID, and a truthful detail page destination.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- FastAPI
- SQLAlchemy
- Pydantic v2
- Next.js App Router

### Source IDs to use for this phase
S01, S08, S10, S11, S12, S14, S19



## Files and directories this phase is allowed to create or modify first

- apps/api/app/api/routes/characters.py
- apps/api/app/services/characters.py
- apps/web/app/studio/characters/[publicId]

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create the character base entity in the asset registry. It must reference the accepted prepared images, the originating photoset, the creator actor, and the initial asset state.

### Step 2
Return a stable public ID from the creation endpoint. The web app must redirect to `/studio/characters/[publicId]` and load entirely from API-backed data.

### Step 3
Write history events for character creation and asset linking. The detail page must later surface these events.

### Step 4
Do not create duplicate character records from the same submission. The create action must be idempotent enough to avoid accidental double-submits.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_11.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- character creation endpoint
- public ID route
- history entries
- detail page data load

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
4. `docs/phase_reports/phase_11.md` is updated with exact commands and results.

# Phase 09 build — Photoset ingest screen with drag/drop and thumbnail grid

## Goal

Create the actual ingest screen where the user drags and drops photos, sees thumbnails, receives guidance, and starts the base-character workflow.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- react-dropzone
- Next.js App Router
- Radix Tooltip
- FormData uploads

### Source IDs to use for this phase
S01, S04, S06, S07, S09



## Files and directories this phase is allowed to create or modify first

- apps/web/app/studio/characters/new
- apps/web/components/character-import

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Make `/studio/characters/new` the canonical route for character creation in this rebuild. If a legacy helper route is needed later, it must wrap or redirect to this page.

### Step 2
Use `react-dropzone` for the ingest zone. Support drag-and-drop and click-to-select. Generate local thumbnails with object URLs. Allow removal before upload.

### Step 3
Render the selected photos in a grid with per-image placeholder QC status badges that are later populated by the backend QC pipeline. Do not display fake 'pass' badges before the backend runs.

### Step 4
Add the capture guide panel from Phase 8 beside the ingest grid. The user should be able to check instructions without leaving the ingest screen.

### Step 5
Use the shared tooltip component for every field on the page.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_09.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- drag/drop ingest page
- thumbnail grid
- capture guide integration

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
4. `docs/phase_reports/phase_09.md` is updated with exact commands and results.

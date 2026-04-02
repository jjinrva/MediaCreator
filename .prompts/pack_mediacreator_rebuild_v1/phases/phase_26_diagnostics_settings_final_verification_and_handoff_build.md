# Phase 26 build — Diagnostics, settings, final verification, polish, and handoff

## Goal

Deliver a polished single-user app with diagnostics, truthful settings, full phase verification, installation docs, and an overnight acceptance report.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/TEAM_PRINCIPAL_SYSTEMS_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`
- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Playwright
- pytest
- FastAPI status endpoints
- Makefile

### Source IDs to use for this phase
S04, S08, S10, S17, S31, S37, S40



## Files and directories this phase is allowed to create or modify first

- apps/web/app/studio/settings
- apps/web/app/studio/diagnostics
- docs/verification
- docs/handoff

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create a settings screen for this single-user build that exposes only truthful controls: storage paths (read-only or clearly editable where safe), ComfyUI capability status, Blender capability status, AI Toolkit status, and active paths to model roots. Do not expose unfinished multi-user or permissions settings.

### Step 2
Create a diagnostics screen that can run end-to-end checks on: ingest pipeline, body edit persistence, pose persistence, GLB preview, export availability, LoRA training capability, and generation workflow availability.

### Step 3
Run a final verification sweep that includes API tests, web tests, focused Blender job checks, ComfyUI capability checks, and selected real workflow runs. Produce a final pass/fail matrix.

### Step 4
Update the root README and handoff docs so a human can run the app after the overnight build. Include exact commands, expected directories, and what is working versus what is still intentionally deferred.

### Step 5
Generate the overnight acceptance report. It must state what the app can do by morning and what remains blocked or future-phase.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_26.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- settings screen
- diagnostics screen
- final verify matrix
- handoff docs
- overnight acceptance report

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
4. `docs/phase_reports/phase_26.md` is updated with exact commands and results.

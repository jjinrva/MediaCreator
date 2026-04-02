# Phase 14 build — Numeric body editing UI and persistence loop

## Goal

Make the body parameter model editable in the UI with numeric sliders that persist, reload, and write history correctly.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Radix Slider
- Radix Tooltip
- FastAPI
- Playwright

### Source IDs to use for this phase
S05, S06, S08, S10, S29



## Files and directories this phase is allowed to create or modify first

- apps/web/components/body-editor
- apps/api/app/api/routes/body.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Build the body editor using the shared `NumericSliderField` pattern. Every control must show the numeric value, unit, and an info tooltip. Use backend-provided parameter metadata instead of hard-coding the ranges in the client.

### Step 2
Implement one canonical save path for body edits. The route handler must call a service that updates values, writes a history event, and returns the new canonical state. The client must reload or reconcile from the returned server state, not assume success purely in local memory.

### Step 3
Start with a stable set of real parameters that can be demonstrated by morning: height scale, shoulder width, chest volume, waist width, hip width, upper-arm volume, thigh volume, and calf volume. Keep the schema open for later expansion.

### Step 4
Make the edit loop explicit: move slider → commit → persist → update history → refresh preview. Do not mix autosave and manual-save semantics without a clear rule. In this rebuild, use `onValueCommit` to persist.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_14.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- body editing UI
- body update endpoint
- history-backed save loop

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
4. `docs/phase_reports/phase_14.md` is updated with exact commands and results.

# Phase 05 build — Job orchestration and background worker foundation

## Goal

Create the durable job model and worker execution path that later phases will use for photo prep, Blender work, LoRA training, exports, and rendering.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- PostgreSQL row locking
- SQLAlchemy
- Python worker process

### Source IDs to use for this phase
S17, S18, S08, S10, S11, S19



## Files and directories this phase is allowed to create or modify first

- apps/api/app/services/jobs.py
- apps/worker
- apps/api/app/api/routes/jobs.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Use a database-backed job queue. Do not add Celery. Do not add Redis. Store jobs in PostgreSQL and have the worker claim work with `FOR UPDATE SKIP LOCKED` semantics.

### Step 2
Define canonical job states now: queued, running, failed, completed, canceled. Add progress fields, step name, error summary, started/finished timestamps, and output references.

### Step 3
Create a minimal `/api/v1/jobs/:publicId` read route and a worker loop that can claim a queued job, mark it running, simulate a step transition, and mark it completed or failed. The payload model should support typed job kinds even if only one or two exist initially.

### Step 4
Write all job state transitions through one service layer. Route handlers must not update job rows directly.

### Step 5
Ensure every job transition writes a history event and can later be shown in the UI.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_05.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- jobs table/service
- worker loop
- job detail route
- job transition history

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
4. `docs/phase_reports/phase_05.md` is updated with exact commands and results.

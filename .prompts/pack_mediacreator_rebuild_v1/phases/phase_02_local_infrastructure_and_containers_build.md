# Phase 02 build — Local infrastructure, containers, and developer entrypoints

## Goal

Stand up the local runtime foundations for the app: PostgreSQL, a dedicated worker process, the API, the web app, and container/dev scripts that can be run repeatably.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/TEAM_PRINCIPAL_SYSTEMS_ARCHITECT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Docker Compose
- PostgreSQL 16
- FastAPI
- Next.js
- Python 3.12

### Source IDs to use for this phase
S08, S10, S14, S15, S20



## Files and directories this phase is allowed to create or modify first

- infra/docker-compose.yml
- scripts/dev.sh
- scripts/run-api.sh
- scripts/run-web.sh
- scripts/run-worker.sh

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create `infra/docker-compose.yml` with PostgreSQL as the only mandatory service in this phase. Do not add speculative services yet. The worker, API, and web app run from source during development, not from containers in this phase.

### Step 2
Set database defaults to PostgreSQL 16. Expose it on a non-conflicting host port. Keep the service name simple and use the same database name, user, and password defaults documented in `.env.example`.

### Step 3
Create `make bootstrap`, `make dev`, `make api`, `make web`, and `make worker`. `make dev` should start PostgreSQL if it is not already up, then start the API, web app, and worker in a predictable documented way.

### Step 4
Add `.env.example` entries for database URL, local scratch path, NAS root path, ComfyUI path placeholder, Blender binary path placeholder, and worker concurrency placeholder. Even if later phases refine them, the contract starts here.

### Step 5
Create a FastAPI `/health` endpoint and a simple Next.js landing page that states the system is in single-user mode and not all screens are finished yet. Truthful placeholders are allowed; fake sample data is not.

### Step 6
Create a minimal worker process that can start, log, and exit cleanly even before jobs exist. This phase only proves the worker entrypoint, not full job execution.

### Step 7
Document exactly how to bring the stack up on a clean machine in the root README and in `docs/architecture/local_runtime.md`.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_02.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- docker-compose
- dev scripts
- root landing page
- health endpoint
- worker entrypoint

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
4. `docs/phase_reports/phase_02.md` is updated with exact commands and results.

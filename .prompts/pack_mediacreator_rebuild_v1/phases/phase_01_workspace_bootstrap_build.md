# Phase 01 build — Workspace bootstrap and monorepo foundation

## Goal

Create a clean MediaCreator monorepo with one frontend app, one backend app, one worker app, shared docs, repeatable commands, and a zero-drift directory contract.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/TEAM_PRINCIPAL_SYSTEMS_ARCHITECT.md`
- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Node.js 22 LTS
- pnpm workspaces
- Python 3.12
- FastAPI
- Next.js App Router
- pytest
- Playwright

### Source IDs to use for this phase
S01, S03, S08, S10, S20, S44, S45


## Exact chosen setup for this phase

- Use **pnpm workspaces** for the JavaScript monorepo management.
- Put the backend and worker in separate Python app folders under `apps/`.
- Keep root automation in a `Makefile`.
- Put all long-lived planning artifacts in `docs/`.
- Name the application **MediaCreator** everywhere from the beginning.


## Files and directories this phase is allowed to create or modify first

- apps/web
- apps/api
- apps/worker
- packages/shared-types
- docs
- infra
- scripts
- storage/.gitkeep
- workflows

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Initialize the repository as a monorepo. Use `pnpm-workspace.yaml` at the root. Put the frontend in `apps/web`, the API in `apps/api`, and the worker in `apps/worker`. Create a root `Makefile`, root `.gitignore`, root `.env.example`, root `README.md`, and root `VERSION`.

### Step 2
Create a root `pyproject.toml` only if it is needed for shared Python tooling. Otherwise keep backend Python configuration inside `apps/api/pyproject.toml` and worker Python configuration inside `apps/worker/pyproject.toml`. Do not scatter Python settings in multiple places without need.

### Step 3
Set the app name everywhere to `MediaCreator`. Do not reuse `AutoCharacter` in package names, README text, route labels, page headings, Docker service names, environment variable prefixes, or docs.

### Step 4
Create a root `docs/` structure with `phase_reports/`, `verification/`, `architecture/`, and `capture_guides/`. Create empty placeholder markdown files only for required reports. Do not seed fake content into the runtime app.

### Step 5
Create a root `scripts/` folder with bootstrap-oriented scripts only: local dev startup, backend test runner, web test runner, and a future-safe worker runner. Use bash or Python scripts, whichever is clearer, but make `make` the canonical entrypoint.

### Step 6
Create the root `README.md` so a new developer can bootstrap the repo without looking anywhere else. It must describe: prerequisites, folder structure, how to run the API, how to run the web app, how to run the worker, and what is intentionally not finished yet.

### Step 7
Create a `docs/architecture/repo_contract.md` that freezes the folder contract so later phases do not create duplicate folders or drift into parallel implementations.

### Step 8
Create a `docs/phase_reports/phase_01.md` and a `docs/verification/phase_01_verify.md` template output path, but do not mark the phase complete until the paired verify document passes.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_01.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- Monorepo skeleton
- Makefile
- .env.example
- root README
- repo contract doc

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
4. `docs/phase_reports/phase_01.md` is updated with exact commands and results.

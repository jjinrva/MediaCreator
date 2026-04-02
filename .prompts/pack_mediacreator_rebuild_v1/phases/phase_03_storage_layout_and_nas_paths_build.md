# Phase 03 build — Storage layout, NAS paths, environment contracts

## Goal

Define the canonical storage layout for models, assets, outputs, exports, and scratch work across NAS and local NVMe without ambiguity.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/TEAM_PRINCIPAL_SYSTEMS_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- PostgreSQL metadata
- filesystem
- NAS mount paths

### Source IDs to use for this phase
S14, S15, S16, S20



## Files and directories this phase is allowed to create or modify first

- storage/
- docs/architecture/storage_layout.md

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Define the storage contract now. Canonical, long-lived assets go to the NAS. Short-lived working files and caches go to local NVMe scratch. Never store large binaries in PostgreSQL.

### Step 2
Create a path schema in `.env.example` for at least: NAS root, models root, LoRA root, checkpoints root, uploaded photos root, prepared images root, character assets root, wardrobe root, exports root, renders root, and local scratch root.

### Step 3
Create a small Python storage service module in the backend that resolves paths from environment settings and creates directories lazily. Do not scatter raw `os.path.join` calls across route handlers.

### Step 4
Create a `storage_manifest` concept in docs now, even if the actual table is introduced later. Every stored artifact will later need a database row that points to its path, lineage, and type.

### Step 5
Make the README explicit about the NAS mount requirement and local scratch requirement. The app should run in degraded mode if the NAS is missing, but it must say so truthfully.

### Step 6
Write `docs/architecture/storage_layout.md` describing exactly what lives on NAS, what lives on local scratch, and which folder names are fixed.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_03.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- storage path contract
- storage service
- storage layout docs

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
4. `docs/phase_reports/phase_03.md` is updated with exact commands and results.

# Phase 04 build — Database foundation, IDs, lineage, and migrations

## Goal

Create the base PostgreSQL schema, UUID strategy, Alembic environment, and history/lineage backbone that every later asset type will use.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- PostgreSQL 16
- SQLAlchemy 2
- Alembic
- Pydantic v2

### Source IDs to use for this phase
S11, S12, S13, S14, S15, S16, S17, S18, S19



## Files and directories this phase is allowed to create or modify first

- apps/api/alembic
- apps/api/app/models
- apps/api/app/db

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Initialize Alembic in the backend app and connect it to the SQLAlchemy metadata. Use SQLAlchemy 2 declarative mappings with typed `mapped_column()` fields. Use Alembic autogenerate only to create candidate migrations and then review them by hand before committing.

### Step 2
Adopt UUID/GUID-style identifiers for entities and public IDs. Use PostgreSQL `uuid` columns and `gen_random_uuid()` where a database-generated UUID is appropriate. Keep room for a separate human-readable `handle` field later where needed.

### Step 3
Create the first core tables: `actors`, `assets`, `history_events`, `jobs` (minimal), and `storage_objects` or a similarly named manifest table. The exact names may vary, but there must be one canonical asset registry and one canonical history/event table.

### Step 4
Make `actors` single-user now. Seed one `god` actor or equivalent bootstrap identity so history entries always have a creator/editor reference.

### Step 5
Create lineage fields now: parent asset ID, source asset ID, created by actor, current owner placeholder, and timestamps. Keep the schema future-ready for multi-user without implementing auth in this rebuild.

### Step 6
Write a backend DB session module and a small migration README so later phases do not improvise their own database access patterns.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_04.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- initial migration stack
- actors table
- asset registry
- history backbone
- DB session pattern

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
4. `docs/phase_reports/phase_04.md` is updated with exact commands and results.

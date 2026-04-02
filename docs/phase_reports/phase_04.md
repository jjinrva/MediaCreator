# Phase 04 report

## Status

PASS

## What changed

- Added the backend database foundation under `apps/api/app/db` with a single session pattern and one metadata registry.
- Added typed SQLAlchemy 2 declarative models for `actors`, `assets`, `history_events`, `jobs`, and `storage_objects`.
- Added Alembic configuration plus a reviewed initial migration that creates the base schema, enables `pgcrypto`, and seeds the single `god` actor.
- Added backend migration tests that create temporary PostgreSQL databases, run the migration stack, and round-trip one sample asset plus one history event.
- Updated the API docs and root README with migration commands and corrected the runtime docs now that migrations exist.
- Fixed two implementation issues before final verify:
  - made Alembic paths resolve relative to the config file using `%(here)s`
  - stopped `alembic/env.py` from overwriting test database URLs during migration tests

## Exact commands run

- `make bootstrap-api`
- `make lint`
- `make typecheck`
- `make test-api`
- `cd /opt/MediaCreator/apps/api && .venv/bin/alembic -c alembic.ini heads`
- `cd /opt/MediaCreator/apps/api && .venv/bin/python - <<'PY' ... ScriptDirectory.from_config(Config(...)) ... PY`
- `docker compose -f /opt/MediaCreator/infra/docker-compose.yml up -d postgres && /opt/MediaCreator/apps/api/.venv/bin/alembic -c /opt/MediaCreator/apps/api/alembic.ini upgrade head && /opt/MediaCreator/apps/api/.venv/bin/alembic -c /opt/MediaCreator/apps/api/alembic.ini downgrade base && /opt/MediaCreator/apps/api/.venv/bin/alembic -c /opt/MediaCreator/apps/api/alembic.ini upgrade head`
- `cd /opt/MediaCreator/apps/api && .venv/bin/python - <<'PY' ... inspect(engine) ... SELECT handle, is_system FROM actors WHERE handle = 'god' ... Base.metadata.tables ... PY`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Tests that passed

- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Remaining risks

- Migration behavior depends on PostgreSQL availability from Phase 02.
- The seeded single-user actor exists, but no auth or multi-user ownership workflows exist yet by design.
- The jobs table is intentionally minimal and does not implement dequeue behavior yet.

## Next phase may start

Yes. Phase 04 verification passed, so Phase 05 may start.

# Phase 04 verification

## Scope verified

- First Alembic migration round-trip on PostgreSQL
- UUID-backed schema columns and `gen_random_uuid()` defaults
- Seeded `god` actor query
- Sample asset and history-event round trip through backend tests
- Alembic metadata loading from the full SQLAlchemy registry
- Absence of duplicate asset-registry or history tables
- Required backend/frontend regression gates

## Commands run

- `docker compose -f /opt/MediaCreator/infra/docker-compose.yml up -d postgres && /opt/MediaCreator/apps/api/.venv/bin/alembic -c /opt/MediaCreator/apps/api/alembic.ini upgrade head && /opt/MediaCreator/apps/api/.venv/bin/alembic -c /opt/MediaCreator/apps/api/alembic.ini downgrade base && /opt/MediaCreator/apps/api/.venv/bin/alembic -c /opt/MediaCreator/apps/api/alembic.ini upgrade head`
- `cd /opt/MediaCreator/apps/api && .venv/bin/python - <<'PY' ... inspect(engine) ... SELECT handle, is_system FROM actors WHERE handle = 'god' ... Base.metadata.tables ... PY`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Files changed in the phase

- `.env.example`
- `README.md`
- `docs/architecture/local_runtime.md`
- `docs/phase_reports/phase_04.md`
- `docs/verification/phase_04_verify.md`
- `apps/api/pyproject.toml`
- `apps/api/alembic.ini`
- `apps/api/alembic/README.md`
- `apps/api/alembic/env.py`
- `apps/api/alembic/script.py.mako`
- `apps/api/alembic/versions/0001_initial_foundation.py`
- `apps/api/app/db/base.py`
- `apps/api/app/db/base_class.py`
- `apps/api/app/db/session.py`
- `apps/api/app/db/settings.py`
- `apps/api/app/models/__init__.py`
- `apps/api/app/models/mixins.py`
- `apps/api/app/models/actor.py`
- `apps/api/app/models/asset.py`
- `apps/api/app/models/history_event.py`
- `apps/api/app/models/job.py`
- `apps/api/app/models/storage_object.py`
- `apps/api/tests/test_db_migrations.py`

## Results

- PASS: the first migration upgraded, downgraded, and upgraded again successfully against PostgreSQL.
- PASS: direct schema inspection showed `UUID` columns on `actors.id`, `actors.public_id`, `assets.id`, and `assets.public_id`.
- PASS: querying `actors` after migration returned the seeded `god` actor with `is_system = true`.
- PASS: backend migration tests created and queried one sample asset and one history event successfully.
- PASS: `Base.metadata.tables` loaded `actors`, `assets`, `history_events`, `jobs`, and `storage_objects`, and Alembic discovered the `0001_initial_foundation` head.
- PASS: the live table list contained only `actors`, `assets`, `history_events`, `jobs`, `storage_objects`, and `alembic_version`, so there are no duplicate asset/history registry tables.
- PASS: `make test-api`, `make test-web`, `make lint`, and `make typecheck` all completed successfully.

## PASS/FAIL decision

PASS

## Remaining risks

- The development database is now migrated to the Phase 04 head and later phases must evolve it through Alembic rather than ad-hoc SQL.
- The schema is intentionally minimal; queue locking behavior, richer lineage, and higher-level asset domain tables come later.
- Playwright still emits `NO_COLOR` warnings in this environment, but the smoke path passes.

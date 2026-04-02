# Alembic usage

MediaCreator uses one SQLAlchemy metadata registry in `app.db.base.Base.metadata`.

## Commands

Run from `/opt/MediaCreator/apps/api`:

```bash
.venv/bin/alembic -c alembic.ini upgrade head
.venv/bin/alembic -c alembic.ini downgrade base
```

## Rules

- Add new tables and columns through SQLAlchemy models first.
- Use Alembic autogenerate only to produce candidate migrations.
- Review generated migrations by hand before committing them.
- Do not create ad-hoc engines or metadata registries outside `app.db`.

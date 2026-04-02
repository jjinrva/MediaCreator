from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import Session

from alembic import command
from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.job import Job
from tests.db_test_utils import (
    TEST_BASE_DATABASE_URL,
    alembic_config,
    create_database,
    drop_database,
    temp_database_url,
)


def test_initial_migration_runs_up_and_down() -> None:
    database_url, database_name = temp_database_url(TEST_BASE_DATABASE_URL, "migrate")
    create_database(TEST_BASE_DATABASE_URL, database_name)

    try:
        config = alembic_config(database_url)
        command.upgrade(config, "head")

        engine = create_engine(database_url)
        inspector = inspect(engine)
        assert {"actors", "assets", "history_events", "jobs", "storage_objects"}.issubset(
            set(inspector.get_table_names())
        )
        actor_columns = {
            column["name"]: column["type"] for column in inspector.get_columns("actors")
        }
        job_columns = {column["name"] for column in inspector.get_columns("jobs")}
        history_columns = {column["name"] for column in inspector.get_columns("history_events")}
        assert actor_columns["id"].__class__.__name__ == "UUID"
        assert actor_columns["public_id"].__class__.__name__ == "UUID"
        assert {
            "progress_percent",
            "step_name",
            "error_summary",
            "output_asset_id",
            "output_storage_object_id",
        }.issubset(job_columns)
        assert "job_id" in history_columns

        with engine.connect() as connection:
            actor_row = connection.execute(
                text("SELECT handle, is_system FROM actors WHERE handle = 'god'")
            ).one()
            assert actor_row.handle == "god"
            assert actor_row.is_system is True

        engine.dispose()

        command.downgrade(config, "base")
        engine = create_engine(database_url)
        inspector = inspect(engine)
        assert not {
            "actors",
            "assets",
            "history_events",
            "jobs",
            "storage_objects",
        }.intersection(inspector.get_table_names())
        engine.dispose()
    finally:
        drop_database(TEST_BASE_DATABASE_URL, database_name)


def test_sample_asset_and_history_event_round_trip() -> None:
    database_url, database_name = temp_database_url(TEST_BASE_DATABASE_URL, "history")
    create_database(TEST_BASE_DATABASE_URL, database_name)

    try:
        config = alembic_config(database_url)
        command.upgrade(config, "head")

        engine = create_engine(database_url)
        with Session(engine) as session:
            god_id = session.execute(
                text("SELECT id FROM actors WHERE handle = 'god'")
            ).scalar_one()
            job = Job(
                job_type="noop",
                status="queued",
                payload={"kind": "noop", "note": "Round-trip job"},
                created_by_actor_id=god_id,
                current_owner_actor_id=god_id,
                progress_percent=0,
                step_name="queued",
            )
            session.add(job)
            session.flush()

            asset = Asset(asset_type="character", created_by_actor_id=god_id)
            session.add(asset)
            session.flush()

            event = HistoryEvent(
                event_type="asset.created",
                details={"asset_type": "character"},
                actor_id=god_id,
                asset_id=asset.id,
                job_id=job.id,
            )
            session.add(event)
            session.commit()

            stored_asset = session.get(Asset, asset.id)
            stored_job = session.get(Job, job.id)
            stored_event = session.scalar(
                select(HistoryEvent).where(HistoryEvent.asset_id == asset.id)
            )
            assert stored_asset is not None
            assert stored_asset.public_id is not None
            assert stored_job is not None
            assert stored_job.progress_percent == 0
            assert stored_job.step_name == "queued"
            assert stored_event is not None
            assert stored_event.event_type == "asset.created"
            assert stored_event.job_id == job.id

        engine.dispose()
    finally:
        drop_database(TEST_BASE_DATABASE_URL, database_name)

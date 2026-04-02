from collections.abc import Callable, Generator
from datetime import timedelta
from threading import Event, Thread

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.main import app
from app.models.history_event import HistoryEvent
from app.models.job import Job
from app.services.jobs import (
    claim_next_queued_job,
    complete_job,
    enqueue_job,
    get_job_by_public_id,
    get_service_heartbeat_payload,
    get_system_actor_id,
    run_worker_once,
    upsert_service_heartbeat,
)
from tests.db_test_utils import migrated_database


def _session_factory(database_url: str) -> tuple[Engine, sessionmaker[Session]]:
    engine = create_engine(database_url, pool_pre_ping=True)
    return engine, sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _override_db_session(
    session_factory: sessionmaker[Session],
) -> Callable[[], Generator[Session, None, None]]:
    def _dependency() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    return _dependency


def test_run_worker_once_processes_exactly_one_job_per_cycle() -> None:
    with migrated_database("jobs_once") as database_url:
        engine, session_factory = _session_factory(database_url)
        try:
            with session_factory() as session, session.begin():
                actor_id = get_system_actor_id(session)
                first_job = enqueue_job(session, actor_id, {"kind": "noop"})
                second_job = enqueue_job(session, actor_id, {"kind": "noop"})
                first_public_id = first_job.public_id
                second_public_id = second_job.public_id

            result = run_worker_once(session_factory)

            assert result == "completed"

            with session_factory() as session:
                stored_first_job = get_job_by_public_id(session, first_public_id)
                stored_second_job = get_job_by_public_id(session, second_public_id)
                assert stored_first_job is not None
                assert stored_second_job is not None
                assert stored_first_job.status == "completed"
                assert stored_second_job.status == "queued"
        finally:
            engine.dispose()


def test_run_worker_once_skip_locked_prevents_double_execution() -> None:
    with migrated_database("jobs_skip_locked") as database_url:
        engine, session_factory = _session_factory(database_url)
        try:
            with session_factory() as session, session.begin():
                actor_id = get_system_actor_id(session)
                job = enqueue_job(session, actor_id, {"kind": "noop"})
                job_public_id = job.public_id

            first_claimed = Event()
            release_first_worker = Event()
            thread_errors: list[BaseException] = []
            results: dict[str, str] = {}

            def hold_claim(_job: Job) -> None:
                first_claimed.set()
                assert release_first_worker.wait(timeout=5)

            def worker_target(
                name: str,
                on_claim: Callable[[Job], None] | None = None,
            ) -> None:
                try:
                    results[name] = run_worker_once(session_factory, on_claim=on_claim)
                except BaseException as exc:  # pragma: no cover - surfaced below
                    thread_errors.append(exc)

            first_worker = Thread(
                target=worker_target,
                args=("first", hold_claim),
                daemon=True,
            )
            first_worker.start()
            assert first_claimed.wait(timeout=5)

            second_worker = Thread(target=worker_target, args=("second",), daemon=True)
            second_worker.start()
            second_worker.join(timeout=5)

            assert not second_worker.is_alive()

            release_first_worker.set()
            first_worker.join(timeout=5)

            assert not first_worker.is_alive()
            assert not thread_errors
            assert results == {"first": "completed", "second": "idle"}

            with session_factory() as session:
                stored_job = get_job_by_public_id(session, job_public_id)
                assert stored_job is not None
                running_events = session.scalars(
                    select(HistoryEvent).where(
                        HistoryEvent.job_id == stored_job.id,
                        HistoryEvent.event_type == "job.running",
                    )
                ).all()
                assert stored_job.status == "completed"
                assert len(running_events) == 1
        finally:
            engine.dispose()


def test_job_detail_api_reflects_state_transitions() -> None:
    with migrated_database("jobs_api") as database_url:
        engine, session_factory = _session_factory(database_url)
        app.dependency_overrides[get_db_session] = _override_db_session(session_factory)

        try:
            with session_factory() as session, session.begin():
                actor_id = get_system_actor_id(session)
                queued_job = enqueue_job(
                    session,
                    actor_id,
                    {"kind": "noop", "note": "API-visible queue state"},
                )
                queued_public_id = queued_job.public_id

            with TestClient(app) as client:
                queued_response = client.get(f"/api/v1/jobs/{queued_public_id}")
                assert queued_response.status_code == 200
                assert queued_response.json()["status"] == "queued"
                assert queued_response.json()["progress_percent"] == 0
                assert queued_response.json()["step_name"] == "queued"

                with session_factory() as session, session.begin():
                    actor_id = get_system_actor_id(session)
                    claim_next_queued_job(session, actor_id)

                running_response = client.get(f"/api/v1/jobs/{queued_public_id}")
                assert running_response.status_code == 200
                assert running_response.json()["status"] == "running"
                assert running_response.json()["progress_percent"] == 10
                assert running_response.json()["step_name"] == "claimed"
                assert running_response.json()["started_at"] is not None

                with session_factory() as session, session.begin():
                    actor_id = get_system_actor_id(session)
                    running_job = get_job_by_public_id(session, queued_public_id)
                    assert running_job is not None
                    complete_job(session, actor_id, running_job)

                completed_response = client.get(f"/api/v1/jobs/{queued_public_id}")
                assert completed_response.status_code == 200
                assert completed_response.json()["status"] == "completed"
                assert completed_response.json()["progress_percent"] == 100
                assert completed_response.json()["step_name"] == "completed"
                assert completed_response.json()["finished_at"] is not None

                with session_factory() as session, session.begin():
                    actor_id = get_system_actor_id(session)
                    failing_job = enqueue_job(
                        session,
                        actor_id,
                        {
                            "kind": "failing-noop",
                            "error_summary": "Intentional test failure",
                        },
                    )
                    failing_public_id = failing_job.public_id

                assert run_worker_once(session_factory) == "failed"

                failed_response = client.get(f"/api/v1/jobs/{failing_public_id}")
                assert failed_response.status_code == 200
                assert failed_response.json()["status"] == "failed"
                assert failed_response.json()["step_name"] == "failed"
                assert failed_response.json()["error_summary"] == "Intentional test failure"
        finally:
            app.dependency_overrides.clear()
            engine.dispose()


def test_job_history_events_cover_completed_and_failed_paths() -> None:
    with migrated_database("jobs_history") as database_url:
        engine, session_factory = _session_factory(database_url)
        try:
            with session_factory() as session, session.begin():
                actor_id = get_system_actor_id(session)
                completed_job = enqueue_job(session, actor_id, {"kind": "noop"})
                failed_job = enqueue_job(
                    session,
                    actor_id,
                    {
                        "kind": "failing-noop",
                        "error_summary": "Fail path verification",
                    },
                )
                completed_job_id = completed_job.id
                failed_job_id = failed_job.id

            assert run_worker_once(session_factory) == "completed"
            assert run_worker_once(session_factory) == "failed"

            with session_factory() as session:
                completed_events = session.scalars(
                    select(HistoryEvent)
                    .where(HistoryEvent.job_id == completed_job_id)
                    .order_by(HistoryEvent.created_at.asc())
                ).all()
                failed_events = session.scalars(
                    select(HistoryEvent)
                    .where(HistoryEvent.job_id == failed_job_id)
                    .order_by(HistoryEvent.created_at.asc())
                ).all()

                assert [event.event_type for event in completed_events] == [
                    "job.queued",
                    "job.running",
                    "job.progressed",
                    "job.completed",
                ]
                assert [event.event_type for event in failed_events] == [
                    "job.queued",
                    "job.running",
                    "job.progressed",
                    "job.failed",
                ]
                assert completed_events[-1].details["status"] == "completed"
                assert failed_events[-1].details["status"] == "failed"
                assert failed_events[-1].details["error_summary"] == "Fail path verification"
        finally:
            engine.dispose()


def test_service_heartbeat_payload_marks_worker_ready_and_stale() -> None:
    with migrated_database("service_heartbeat_payload") as database_url:
        engine, session_factory = _session_factory(database_url)
        try:
            with session_factory() as session, session.begin():
                missing_payload = get_service_heartbeat_payload(session, "worker")
                assert missing_payload["status"] == "offline"

                heartbeat = upsert_service_heartbeat(
                    session,
                    service_name="worker",
                    detail="polling",
                )
                ready_payload = get_service_heartbeat_payload(session, "worker")
                assert ready_payload["status"] == "ready"
                assert ready_payload["seconds_since_heartbeat"] == 0
                assert ready_payload["last_seen_at"] == heartbeat.last_seen_at

                heartbeat.last_seen_at = heartbeat.last_seen_at - timedelta(seconds=30)
                session.flush()

                stale_payload = get_service_heartbeat_payload(session, "worker")
                assert stale_payload["status"] == "stale"
                seconds_since_heartbeat = stale_payload["seconds_since_heartbeat"]
                assert isinstance(seconds_since_heartbeat, int)
                assert seconds_since_heartbeat >= 30
                assert "stale" in str(stale_payload["detail"])
        finally:
            engine.dispose()

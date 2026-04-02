import logging
import os
import signal
from threading import Event

from app.db.session import get_session_factory
from app.services.jobs import WORKER_SERVICE_NAME, run_worker_once, upsert_service_heartbeat
from pydantic import BaseModel


class WorkerBootstrapStatus(BaseModel):
    application: str = "MediaCreator"
    service: str = "worker"
    status: str = "job-worker-ready"
    detail: str = "Database-backed dequeue is active through PostgreSQL row locking."
    concurrency_configured: int
    dequeue_strategy: str = "postgres-skip-locked"
    poll_interval_seconds: float


shutdown_requested = Event()


def _handle_shutdown(signum: int, _frame: object) -> None:
    logging.getLogger("mediacreator.worker").info("Shutdown signal %s received.", signum)
    shutdown_requested.set()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("mediacreator.worker")

    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    status = WorkerBootstrapStatus(
        concurrency_configured=int(os.getenv("MEDIACREATOR_WORKER_CONCURRENCY", "1")),
        poll_interval_seconds=float(os.getenv("MEDIACREATOR_WORKER_POLL_SECONDS", "1")),
    )
    session_factory = get_session_factory()
    logger.info("Worker bootstrap status: %s", status.model_dump_json())
    logger.info("Worker polling loop is active.")

    while not shutdown_requested.is_set():
        with session_factory() as session:
            with session.begin():
                upsert_service_heartbeat(
                    session,
                    service_name=WORKER_SERVICE_NAME,
                    detail="polling",
                )
        result = run_worker_once(session_factory)
        if result != "idle":
            logger.info("Worker cycle result: %s", result)
        shutdown_requested.wait(timeout=status.poll_interval_seconds)

    logger.info("Worker exited cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

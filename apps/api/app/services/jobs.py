import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter
from sqlalchemy import Select, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.actor import Actor
from app.models.history_event import HistoryEvent
from app.models.job import Job


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELED = "canceled"


class NoopJobPayload(BaseModel):
    kind: Literal["noop"] = "noop"
    note: str = "Simulated job execution"


class FailingNoopJobPayload(BaseModel):
    kind: Literal["failing-noop"] = "failing-noop"
    error_summary: str = "Simulated job failure"


class BlenderPreviewExportJobPayload(BaseModel):
    kind: Literal["blender-preview-export"] = "blender-preview-export"
    character_public_id: uuid.UUID
    input_asset_paths: list[str]
    body_values: dict[str, float]
    pose_values: dict[str, float]
    output_preview_glb_path: str
    output_final_glb_path: str
    export_root_class: str
    workflow_path: str
    script_path: str


JobPayload = Annotated[
    NoopJobPayload | FailingNoopJobPayload | BlenderPreviewExportJobPayload,
    Field(discriminator="kind"),
]
JOB_PAYLOAD_ADAPTER: TypeAdapter[JobPayload] = TypeAdapter(JobPayload)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _job_query() -> Select[tuple[Job]]:
    return select(Job).order_by(Job.created_at.asc())


def _append_job_history_event(
    session: Session,
    actor_id: uuid.UUID,
    job: Job,
    event_type: str,
    details: dict[str, object],
) -> HistoryEvent:
    history_event = HistoryEvent(
        event_type=event_type,
        details=details,
        actor_id=actor_id,
        job_id=job.id,
        asset_id=job.output_asset_id,
    )
    session.add(history_event)
    return history_event


def get_system_actor_id(session: Session, handle: str = "god") -> uuid.UUID:
    actor_id = session.execute(select(Actor.id).where(Actor.handle == handle)).scalar_one()
    return actor_id


def enqueue_job(
    session: Session,
    actor_id: uuid.UUID,
    payload: dict[str, object],
    *,
    output_asset_id: uuid.UUID | None = None,
) -> Job:
    validated_payload = JOB_PAYLOAD_ADAPTER.validate_python(payload)
    job = Job(
        job_type=validated_payload.kind,
        status=JobState.QUEUED,
        payload=validated_payload.model_dump(mode="json"),
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
        progress_percent=0,
        step_name="queued",
        output_asset_id=output_asset_id,
    )
    session.add(job)
    session.flush()
    _append_job_history_event(
        session,
        actor_id,
        job,
        "job.queued",
        {"status": JobState.QUEUED, "job_type": job.job_type},
    )
    return job


def get_job_by_public_id(session: Session, public_id: uuid.UUID) -> Job | None:
    return session.execute(_job_query().where(Job.public_id == public_id)).scalar_one_or_none()


def claim_next_queued_job(session: Session, actor_id: uuid.UUID) -> Job | None:
    job = session.execute(
        _job_query()
        .where(Job.status == JobState.QUEUED)
        .limit(1)
        .with_for_update(skip_locked=True)
    ).scalar_one_or_none()
    if job is None:
        return None

    job.status = JobState.RUNNING
    job.progress_percent = 10
    job.step_name = "claimed"
    job.started_at = _now()
    job.current_owner_actor_id = actor_id
    _append_job_history_event(
        session,
        actor_id,
        job,
        "job.running",
        {"status": JobState.RUNNING, "job_type": job.job_type, "step_name": job.step_name},
    )
    session.flush()
    return job


def complete_job(
    session: Session,
    actor_id: uuid.UUID,
    job: Job,
    output_asset_id: uuid.UUID | None = None,
    output_storage_object_id: uuid.UUID | None = None,
) -> Job:
    job.status = JobState.COMPLETED
    job.progress_percent = 100
    job.step_name = "completed"
    job.error_summary = None
    job.finished_at = _now()
    job.output_asset_id = output_asset_id
    job.output_storage_object_id = output_storage_object_id
    _append_job_history_event(
        session,
        actor_id,
        job,
        "job.completed",
        {"status": JobState.COMPLETED, "job_type": job.job_type},
    )
    session.flush()
    return job


def fail_job(session: Session, actor_id: uuid.UUID, job: Job, error_summary: str) -> Job:
    job.status = JobState.FAILED
    job.progress_percent = 100
    job.step_name = "failed"
    job.error_summary = error_summary
    job.finished_at = _now()
    _append_job_history_event(
        session,
        actor_id,
        job,
        "job.failed",
        {"status": JobState.FAILED, "job_type": job.job_type, "error_summary": error_summary},
    )
    session.flush()
    return job


def cancel_job(session: Session, actor_id: uuid.UUID, job: Job) -> Job:
    job.status = JobState.CANCELED
    job.progress_percent = 100
    job.step_name = "canceled"
    job.error_summary = None
    job.finished_at = _now()
    _append_job_history_event(
        session,
        actor_id,
        job,
        "job.canceled",
        {"status": JobState.CANCELED, "job_type": job.job_type},
    )
    session.flush()
    return job


def advance_job_progress(
    session: Session,
    actor_id: uuid.UUID,
    job: Job,
    *,
    step_name: str,
    progress_percent: int,
) -> Job:
    job.step_name = step_name
    job.progress_percent = progress_percent
    _append_job_history_event(
        session,
        actor_id,
        job,
        "job.progressed",
        {
            "status": job.status,
            "job_type": job.job_type,
            "step_name": step_name,
            "progress_percent": progress_percent,
        },
    )
    session.flush()
    return job


def run_worker_once(
    session_factory: sessionmaker[Session],
    on_claim: Callable[[Job], None] | None = None,
) -> str:
    claimed_public_id: uuid.UUID | None = None

    with session_factory() as session:
        with session.begin():
            actor_id = get_system_actor_id(session)
            claimed_job = claim_next_queued_job(session, actor_id)
            if claimed_job is None:
                return "idle"
            claimed_public_id = claimed_job.public_id
            if on_claim is not None:
                on_claim(claimed_job)

    assert claimed_public_id is not None

    with session_factory() as session:
        with session.begin():
            actor_id = get_system_actor_id(session)
            job = get_job_by_public_id(session, claimed_public_id)
            if job is None:
                return "missing"

            validated_payload = JOB_PAYLOAD_ADAPTER.validate_python(job.payload)
            advance_job_progress(
                session,
                actor_id,
                job,
                step_name="simulating",
                progress_percent=75,
            )

            if validated_payload.kind == "failing-noop":
                fail_job(session, actor_id, job, validated_payload.error_summary)
                return "failed"

            if validated_payload.kind == "blender-preview-export":
                from app.services.blender_runtime import execute_blender_preview_export_job

                advance_job_progress(
                    session,
                    actor_id,
                    job,
                    step_name="running-blender-export",
                    progress_percent=75,
                )
                output_storage_object_id = execute_blender_preview_export_job(
                    session,
                    job,
                    validated_payload,
                )
                complete_job(
                    session,
                    actor_id,
                    job,
                    output_asset_id=job.output_asset_id,
                    output_storage_object_id=output_storage_object_id,
                )
                return "completed"

            complete_job(session, actor_id, job)
            return "completed"

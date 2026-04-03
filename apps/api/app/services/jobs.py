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
from app.models.service_heartbeat import ServiceHeartbeat

WORKER_SERVICE_NAME = "worker"
DEFAULT_WORKER_HEARTBEAT_STALE_AFTER_SECONDS = 15


def _default_ingest_bucket_counts() -> dict[str, int]:
    return {
        "lora_only": 0,
        "body_only": 0,
        "both": 0,
        "rejected": 0,
    }


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


class PhotosetIngestJobPayload(BaseModel):
    class StagedUpload(BaseModel):
        byte_size: int
        filename: str
        media_type: str
        staged_path: str

    kind: Literal["photoset-ingest"] = "photoset-ingest"
    character_label: str
    staged_uploads: list[StagedUpload]
    total_files: int
    processed_files: int = 0
    bucket_counts: dict[str, int] = Field(default_factory=_default_ingest_bucket_counts)
    photoset_public_id: uuid.UUID


class BlenderPreviewExportJobPayload(BaseModel):
    kind: Literal["blender-preview-export"] = "blender-preview-export"
    character_public_id: uuid.UUID
    input_asset_paths: list[str]
    body_values: dict[str, float]
    pose_values: dict[str, float]
    motion_clip_name: str | None = None
    motion_duration_seconds: float | None = None
    motion_payload_path: str | None = None
    base_color_texture_path: str | None
    texture_fidelity: str
    output_preview_glb_path: str
    output_final_glb_path: str
    export_root_class: str
    workflow_path: str
    script_path: str


class HighDetailReconstructionJobPayload(BaseModel):
    kind: Literal["high-detail-reconstruction"] = "high-detail-reconstruction"
    character_public_id: uuid.UUID
    capture_entry_public_ids: list[uuid.UUID]
    capture_input_paths: list[str]
    accepted_entry_count: int
    body_qualified_entry_count: int
    reconstruction_strategy: str
    detail_level_target: str
    output_detail_prep_path: str
    output_root_class: str


class LoraTrainingJobPayload(BaseModel):
    kind: Literal["lora-train-ai-toolkit"] = "lora-train-ai-toolkit"
    character_public_id: uuid.UUID
    ai_toolkit_bin: str
    dataset_manifest_path: str
    output_lora_path: str
    prompt_handle: str
    training_config_path: str


class GenerationProofImageJobPayload(BaseModel):
    kind: Literal["generation-proof-image"] = "generation-proof-image"
    generation_request_public_id: uuid.UUID
    character_public_id: uuid.UUID | None = None
    local_lora_registry_public_id: uuid.UUID | None = None
    external_lora_registry_public_id: uuid.UUID | None = None
    expanded_prompt: str
    workflow_id: str
    workflow_path: str
    output_image_path: str
    output_root_class: str


class VideoRenderJobPayload(BaseModel):
    kind: Literal["character-motion-video-render"] = "character-motion-video-render"
    character_public_id: uuid.UUID
    video_asset_public_id: uuid.UUID
    motion_asset_public_id: uuid.UUID
    motion_name: str
    motion_payload_path: str
    body_values: dict[str, float]
    pose_values: dict[str, float]
    face_values: dict[str, float] | None
    resolution_width: int
    resolution_height: int
    duration_seconds: float
    fps: int
    output_video_path: str
    render_root_class: str
    workflow_path: str
    script_path: str


JobPayload = Annotated[
    PhotosetIngestJobPayload
    | NoopJobPayload
    | FailingNoopJobPayload
    | BlenderPreviewExportJobPayload
    | HighDetailReconstructionJobPayload
    | LoraTrainingJobPayload
    | GenerationProofImageJobPayload
    | VideoRenderJobPayload,
    Field(discriminator="kind"),
]
JOB_PAYLOAD_ADAPTER: TypeAdapter[JobPayload] = TypeAdapter(JobPayload)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _job_query() -> Select[tuple[Job]]:
    return select(Job).order_by(Job.created_at.asc())


def _service_heartbeat_query() -> Select[tuple[ServiceHeartbeat]]:
    return select(ServiceHeartbeat).order_by(ServiceHeartbeat.created_at.asc())


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


def _job_progress_snapshot(job: Job) -> dict[str, object]:
    details: dict[str, object] = {
        "status": job.status,
        "job_type": job.job_type,
        "step_name": job.step_name,
        "progress_percent": job.progress_percent,
    }
    total_files = job.payload.get("total_files")
    processed_files = job.payload.get("processed_files")
    bucket_counts = job.payload.get("bucket_counts")
    if isinstance(total_files, int):
        details["total_files"] = total_files
    if isinstance(processed_files, int):
        details["processed_files"] = processed_files
    if isinstance(bucket_counts, dict):
        details["bucket_counts"] = bucket_counts
    return details


def get_system_actor_id(session: Session, handle: str = "god") -> uuid.UUID:
    actor_id = session.execute(select(Actor.id).where(Actor.handle == handle)).scalar_one()
    return actor_id


def get_service_heartbeat(
    session: Session,
    service_name: str,
) -> ServiceHeartbeat | None:
    return session.execute(
        _service_heartbeat_query().where(ServiceHeartbeat.service_name == service_name)
    ).scalar_one_or_none()


def upsert_service_heartbeat(
    session: Session,
    *,
    service_name: str,
    detail: str,
) -> ServiceHeartbeat:
    heartbeat = get_service_heartbeat(session, service_name)
    if heartbeat is None:
        heartbeat = ServiceHeartbeat(
            service_name=service_name,
            detail=detail,
            last_seen_at=_now(),
        )
        session.add(heartbeat)
    else:
        heartbeat.detail = detail
        heartbeat.last_seen_at = _now()
    session.flush()
    return heartbeat


def get_service_heartbeat_payload(
    session: Session,
    service_name: str,
    *,
    stale_after_seconds: int = DEFAULT_WORKER_HEARTBEAT_STALE_AFTER_SECONDS,
) -> dict[str, object]:
    heartbeat = get_service_heartbeat(session, service_name)
    if heartbeat is None:
        return {
            "service_name": service_name,
            "status": "offline",
            "detail": f"No heartbeat has been recorded for the '{service_name}' service yet.",
            "last_seen_at": None,
            "seconds_since_heartbeat": None,
            "stale_after_seconds": stale_after_seconds,
        }

    seconds_since_heartbeat = max(
        0,
        int((_now() - heartbeat.last_seen_at).total_seconds()),
    )
    if seconds_since_heartbeat > stale_after_seconds:
        status = "stale"
        detail = (
            f"The '{service_name}' heartbeat is stale. Last seen "
            f"{seconds_since_heartbeat}s ago while reporting '{heartbeat.detail}'."
        )
    else:
        status = "ready"
        detail = (
            f"The '{service_name}' heartbeat is current and reports '{heartbeat.detail}'."
        )

    return {
        "service_name": service_name,
        "status": status,
        "detail": detail,
        "last_seen_at": heartbeat.last_seen_at,
        "seconds_since_heartbeat": seconds_since_heartbeat,
        "stale_after_seconds": stale_after_seconds,
    }


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
        _job_progress_snapshot(job),
    )
    return job


def get_job_by_public_id(session: Session, public_id: uuid.UUID) -> Job | None:
    return session.execute(_job_query().where(Job.public_id == public_id)).scalar_one_or_none()


def update_job_payload(
    session: Session,
    job: Job,
    **payload_updates: object,
) -> Job:
    merged_payload = dict(job.payload)
    merged_payload.update(payload_updates)
    validated_payload = JOB_PAYLOAD_ADAPTER.validate_python(merged_payload)
    job.payload = validated_payload.model_dump(mode="json")
    session.flush()
    return job


def start_job(
    session: Session,
    actor_id: uuid.UUID,
    job: Job,
    *,
    step_name: str,
    progress_percent: int,
) -> Job:
    job.status = JobState.RUNNING
    job.progress_percent = progress_percent
    job.step_name = step_name
    job.error_summary = None
    if job.started_at is None:
        job.started_at = _now()
    _append_job_history_event(
        session,
        actor_id,
        job,
        "job.running",
        _job_progress_snapshot(job),
    )
    session.flush()
    return job


def get_job_history(session: Session, job_id: uuid.UUID) -> list[HistoryEvent]:
    return list(
        session.execute(
            select(HistoryEvent)
            .where(HistoryEvent.job_id == job_id)
            .order_by(HistoryEvent.created_at.asc())
        ).scalars()
    )


def serialize_job(job: Job, history_events: list[HistoryEvent]) -> dict[str, object]:
    progress: dict[str, object] | None = None
    total_files = job.payload.get("total_files")
    processed_files = job.payload.get("processed_files")
    bucket_counts = job.payload.get("bucket_counts")
    if (
        isinstance(total_files, int)
        or isinstance(processed_files, int)
        or isinstance(bucket_counts, dict)
    ):
        progress = {
            "total_files": total_files if isinstance(total_files, int) else None,
            "processed_files": processed_files if isinstance(processed_files, int) else None,
            "bucket_counts": bucket_counts if isinstance(bucket_counts, dict) else None,
        }

    return {
        "public_id": job.public_id,
        "job_type": job.job_type,
        "status": job.status,
        "progress_percent": job.progress_percent,
        "step_name": job.step_name,
        "error_summary": job.error_summary,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
        "output_asset_id": job.output_asset_id,
        "output_storage_object_id": job.output_storage_object_id,
        "progress": progress,
        "stage_history": [
            {
                "created_at": event.created_at,
                "event_type": event.event_type,
                "status": event.details.get("status"),
                "step_name": event.details.get("step_name"),
                "progress_percent": event.details.get("progress_percent"),
                "total_files": event.details.get("total_files"),
                "processed_files": event.details.get("processed_files"),
                "bucket_counts": event.details.get("bucket_counts"),
            }
            for event in history_events
        ],
    }


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
        _job_progress_snapshot(job),
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
        _job_progress_snapshot(job),
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
        {
            **_job_progress_snapshot(job),
            "error_summary": error_summary,
        },
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
        _job_progress_snapshot(job),
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
        _job_progress_snapshot(job),
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
            if validated_payload.kind == "photoset-ingest":
                from app.services.photo_prep import execute_photoset_ingest_job

                execute_photoset_ingest_job(session, job, validated_payload)
                return "failed" if job.status == JobState.FAILED else "completed"

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

            if validated_payload.kind == "high-detail-reconstruction":
                from app.services.reconstruction import execute_character_reconstruction_job

                advance_job_progress(
                    session,
                    actor_id,
                    job,
                    step_name="running-high-detail-reconstruction",
                    progress_percent=75,
                )
                output_storage_object_id = execute_character_reconstruction_job(
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

            if validated_payload.kind == "lora-train-ai-toolkit":
                from app.services.lora_training import (
                    execute_lora_training_job,
                    mark_lora_training_job_failed,
                )

                advance_job_progress(
                    session,
                    actor_id,
                    job,
                    step_name="running-ai-toolkit-training",
                    progress_percent=75,
                )
                try:
                    output_storage_object_id = execute_lora_training_job(
                        session,
                        job,
                        validated_payload,
                    )
                except Exception as exc:
                    mark_lora_training_job_failed(
                        session,
                        character_public_id=validated_payload.character_public_id,
                        job_public_id=job.public_id,
                        error_summary=str(exc),
                    )
                    fail_job(session, actor_id, job, str(exc))
                    return "failed"

                complete_job(
                    session,
                    actor_id,
                    job,
                    output_asset_id=job.output_asset_id,
                    output_storage_object_id=output_storage_object_id,
                )
                return "completed"

            if validated_payload.kind == "generation-proof-image":
                from app.services.generation_execution import (
                    execute_generation_proof_image_job,
                    mark_generation_proof_image_job_failed,
                )

                advance_job_progress(
                    session,
                    actor_id,
                    job,
                    step_name="running-generation-proof-image",
                    progress_percent=75,
                )
                try:
                    output_storage_object_id = execute_generation_proof_image_job(
                        session,
                        job,
                        validated_payload,
                    )
                except Exception as exc:
                    mark_generation_proof_image_job_failed(session, job, str(exc))
                    fail_job(session, actor_id, job, str(exc))
                    return "failed"

                complete_job(
                    session,
                    actor_id,
                    job,
                    output_asset_id=job.output_asset_id,
                    output_storage_object_id=output_storage_object_id,
                )
                return "completed"

            if validated_payload.kind == "character-motion-video-render":
                from app.services.video_render import (
                    execute_video_render_job,
                    mark_video_render_job_failed,
                )

                advance_job_progress(
                    session,
                    actor_id,
                    job,
                    step_name="running-controlled-video-render",
                    progress_percent=75,
                )
                try:
                    output_storage_object_id = execute_video_render_job(
                        session,
                        job,
                        validated_payload,
                    )
                except Exception as exc:
                    mark_video_render_job_failed(session, job, str(exc))
                    fail_job(session, actor_id, job, str(exc))
                    return "failed"

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

from __future__ import annotations

import hashlib
import os
import subprocess
import uuid
from pathlib import Path
from typing import cast

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.job import Job
from app.models.storage_object import StorageObject
from app.services.body_parameters import get_character_body_parameter_payload
from app.services.characters import get_character_asset, get_character_payload
from app.services.facial_parameters import get_character_facial_parameter_payload
from app.services.jobs import VideoRenderJobPayload, enqueue_job, get_system_actor_id
from app.services.motion_library import get_character_motion_assignment, get_motion_asset
from app.services.pose_state import get_character_pose_state_payload
from app.services.storage_service import resolve_storage_layout

REPO_ROOT = Path(__file__).resolve().parents[4]
BLENDER_SCRIPT_PATH = REPO_ROOT / "workflows" / "blender" / "render_actions.py"
DEFAULT_BLENDER_BIN = Path("/opt/blender-4.5-lts/blender")
DEFAULT_RENDER_WIDTH = 480
DEFAULT_RENDER_HEIGHT = 480
DEFAULT_RENDER_FPS = 24


def _asset_query() -> Select[tuple[Asset]]:
    return select(Asset).order_by(Asset.created_at.asc())


def _history_query() -> Select[tuple[HistoryEvent]]:
    return select(HistoryEvent).order_by(HistoryEvent.created_at.asc())


def _job_query() -> Select[tuple[Job]]:
    return select(Job).order_by(Job.created_at.desc())


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.asc())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_blender_bin() -> Path:
    configured = Path(os.getenv("MEDIACREATOR_BLENDER_BIN", str(DEFAULT_BLENDER_BIN)))
    if not configured.exists():
        raise FileNotFoundError(f"Blender 4.5 LTS is missing at '{configured}'.")
    return configured


def _resolve_render_root() -> tuple[Path, str]:
    layout = resolve_storage_layout()
    if layout.nas_available:
        layout.renders_root.mkdir(parents=True, exist_ok=True)
        return layout.renders_root, "nas"

    fallback_root = layout.scratch_root / "renders"
    fallback_root.mkdir(parents=True, exist_ok=True)
    return fallback_root, "scratch"


def _resolve_payload_root() -> Path:
    layout = resolve_storage_layout()
    payload_root = layout.scratch_root / "video_render"
    payload_root.mkdir(parents=True, exist_ok=True)
    return payload_root


def _record_history_event(
    session: Session,
    actor_id: uuid.UUID,
    *,
    asset_id: uuid.UUID,
    details: dict[str, object],
    event_type: str,
) -> None:
    session.add(
        HistoryEvent(
            actor_id=actor_id,
            asset_id=asset_id,
            details=details,
            event_type=event_type,
        )
    )


def _current_body_values(session: Session, character_public_id: uuid.UUID) -> dict[str, float]:
    payload = get_character_body_parameter_payload(session, character_public_id)
    if payload is None:
        raise LookupError("Character body parameters not found.")
    current_values = cast(dict[str, float], payload["current_values"])
    return {
        key: float(value)
        for key, value in current_values.items()
    }


def _current_pose_values(session: Session, character_public_id: uuid.UUID) -> dict[str, float]:
    payload = get_character_pose_state_payload(session, character_public_id)
    if payload is None:
        raise LookupError("Character pose state not found.")
    current_values = cast(dict[str, float], payload["current_values"])
    return {
        key: float(value)
        for key, value in current_values.items()
    }


def _current_face_values(
    session: Session,
    character_public_id: uuid.UUID,
) -> dict[str, float] | None:
    payload = get_character_facial_parameter_payload(session, character_public_id)
    if payload is None:
        return None
    current_values = cast(dict[str, float], payload["current_values"])
    return {
        key: float(value)
        for key, value in current_values.items()
    }


def _resolve_motion_assignment(
    session: Session,
    character_public_id: uuid.UUID,
) -> tuple[dict[str, object], Asset]:
    assignment = get_character_motion_assignment(session, character_public_id)
    if assignment is None:
        raise LookupError("Character has no assigned motion clip.")

    motion_public_id_raw = assignment.get("motion_asset_public_id")
    if not isinstance(motion_public_id_raw, str):
        raise LookupError("Character motion assignment is missing the motion asset reference.")

    motion_asset = get_motion_asset(session, uuid.UUID(motion_public_id_raw))
    if motion_asset is None:
        raise LookupError("Assigned motion asset not found.")

    return assignment, motion_asset


def _create_video_asset(
    session: Session,
    actor_id: uuid.UUID,
    *,
    character_asset: Asset,
    duration_seconds: float,
    height: int,
    motion_asset: Asset,
    motion_name: str,
    width: int,
) -> Asset:
    video_asset = Asset(
        asset_type="character-motion-video",
        status="queued",
        parent_asset_id=character_asset.id,
        source_asset_id=motion_asset.id,
        created_by_actor_id=actor_id,
        current_owner_actor_id=actor_id,
    )
    session.add(video_asset)
    session.flush()
    _record_history_event(
        session,
        actor_id,
        asset_id=video_asset.id,
        details={
            "character_public_id": str(character_asset.public_id),
            "duration_seconds": duration_seconds,
            "height": height,
            "motion_asset_public_id": str(motion_asset.public_id),
            "motion_name": motion_name,
            "width": width,
        },
        event_type="video.asset_created",
    )
    return video_asset


def queue_character_video_render(
    session: Session,
    character_public_id: uuid.UUID,
    *,
    duration_seconds: float | None,
    height: int = DEFAULT_RENDER_HEIGHT,
    width: int = DEFAULT_RENDER_WIDTH,
) -> Job:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    assignment, motion_asset = _resolve_motion_assignment(session, character_public_id)
    motion_name = cast(str, assignment["motion_name"])
    requested_duration = duration_seconds
    if requested_duration is None:
        duration_value = assignment.get("duration_seconds")
        if not isinstance(duration_value, int | float):
            raise LookupError("Assigned motion clip is missing a duration.")
        requested_duration = float(duration_value)

    render_root, render_root_class = _resolve_render_root()
    actor_id = get_system_actor_id(session)
    video_asset = _create_video_asset(
        session,
        actor_id,
        character_asset=character_asset,
        duration_seconds=requested_duration,
        height=height,
        motion_asset=motion_asset,
        motion_name=motion_name,
        width=width,
    )
    output_root = render_root / "characters" / str(character_public_id) / "videos"
    output_root.mkdir(parents=True, exist_ok=True)

    payload = VideoRenderJobPayload(
        character_public_id=character_public_id,
        video_asset_public_id=video_asset.public_id,
        motion_asset_public_id=motion_asset.public_id,
        motion_name=motion_name,
        motion_payload_path=str(assignment["action_payload_path"]),
        body_values=_current_body_values(session, character_public_id),
        pose_values=_current_pose_values(session, character_public_id),
        face_values=_current_face_values(session, character_public_id),
        resolution_width=width,
        resolution_height=height,
        duration_seconds=requested_duration,
        fps=DEFAULT_RENDER_FPS,
        output_video_path=str(output_root / f"{video_asset.public_id}.mp4"),
        render_root_class=render_root_class,
        workflow_path=str(BLENDER_SCRIPT_PATH),
        script_path=str(BLENDER_SCRIPT_PATH),
    )
    job = enqueue_job(
        session,
        actor_id,
        payload.model_dump(mode="json"),
        output_asset_id=video_asset.id,
    )
    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "duration_seconds": requested_duration,
            "height": height,
            "job_public_id": str(job.public_id),
            "motion_asset_public_id": str(motion_asset.public_id),
            "motion_name": motion_name,
            "video_asset_public_id": str(video_asset.public_id),
            "width": width,
        },
        event_type="video.render_requested",
    )
    return job


def _run_blender_background_job(payload: VideoRenderJobPayload) -> None:
    blender_bin = _resolve_blender_bin()
    payload_root = _resolve_payload_root()
    payload_path = payload_root / f"{payload.video_asset_public_id}-video-render.json"
    payload_path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")

    subprocess.run(
        [
            str(blender_bin),
            "--background",
            "--factory-startup",
            "--python",
            payload.script_path,
            "--",
            str(payload_path),
        ],
        check=True,
        cwd=str(REPO_ROOT),
    )


def _video_storage_object(
    session: Session,
    video_asset_id: uuid.UUID,
) -> StorageObject | None:
    return session.execute(
        _storage_object_query().where(
            StorageObject.source_asset_id == video_asset_id,
            StorageObject.object_type == "character-motion-video-mp4",
        )
    ).scalar_one_or_none()


def _video_storage_object_by_public_id(
    session: Session,
    video_asset_public_id: uuid.UUID,
) -> StorageObject | None:
    video_asset = get_video_asset(session, video_asset_public_id)
    if video_asset is None:
        return None
    return _video_storage_object(session, video_asset.id)


def _character_video_history(session: Session, character_asset_id: uuid.UUID) -> list[HistoryEvent]:
    return list(
        session.scalars(
            select(HistoryEvent)
            .where(
                HistoryEvent.asset_id == character_asset_id,
                HistoryEvent.event_type.like("video.%"),
            )
            .order_by(HistoryEvent.created_at.desc())
        ).all()
    )


def _video_asset_history(session: Session, video_asset_id: uuid.UUID) -> list[HistoryEvent]:
    return list(
        session.scalars(_history_query().where(HistoryEvent.asset_id == video_asset_id)).all()
    )


def _video_asset_created_details(session: Session, video_asset_id: uuid.UUID) -> dict[str, object]:
    for event in _video_asset_history(session, video_asset_id):
        if event.event_type == "video.asset_created":
            return event.details
    raise LookupError("Video asset history is missing the creation event.")


def _latest_video_asset(session: Session, character_asset_id: uuid.UUID) -> Asset | None:
    return session.execute(
        select(Asset)
        .where(
            Asset.asset_type == "character-motion-video",
            Asset.parent_asset_id == character_asset_id,
        )
        .order_by(Asset.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def _latest_video_job(session: Session, video_asset_id: uuid.UUID) -> Job | None:
    return session.execute(
        _job_query().where(
            Job.output_asset_id == video_asset_id,
            Job.job_type == "character-motion-video-render",
        )
    ).scalar_one_or_none()


def _video_job_payload(job: Job | None) -> dict[str, object]:
    if job is None:
        return {
            "detail": "No controlled video render job has been queued yet.",
            "public_id": None,
            "status": "not-queued",
        }

    if job.status == "completed":
        detail = "Latest controlled video render job completed successfully."
    elif job.status == "failed":
        detail = job.error_summary or "Latest controlled video render job failed."
    else:
        detail = f"Latest controlled video render job is {job.status}."

    return {
        "detail": detail,
        "public_id": job.public_id,
        "status": job.status,
    }


def _character_label(session: Session, character_asset: Asset) -> str:
    payload = get_character_payload(session, character_asset.public_id, api_base_url="")
    if payload is None:
        return f"Character {str(character_asset.public_id)[:8]}"
    label = payload.get("label")
    return (
        label
        if isinstance(label, str) and label
        else f"Character {str(character_asset.public_id)[:8]}"
    )


def _latest_video_payload(
    session: Session,
    *,
    api_base_url: str,
    video_asset: Asset | None,
) -> dict[str, object] | None:
    if video_asset is None:
        return None

    created_details = _video_asset_created_details(session, video_asset.id)
    storage_object = _video_storage_object(session, video_asset.id)
    latest_job = _latest_video_job(session, video_asset.id)
    url = None
    file_size_bytes = None
    storage_object_public_id = None
    if storage_object is not None and Path(storage_object.storage_path).exists():
        url = f"{api_base_url}/api/v1/video/assets/{video_asset.public_id}.mp4"
        file_size_bytes = storage_object.byte_size
        storage_object_public_id = storage_object.public_id

    motion_asset_public_id = created_details.get("motion_asset_public_id")
    motion_name = created_details.get("motion_name")
    duration_seconds = created_details.get("duration_seconds")
    height = created_details.get("height")
    width = created_details.get("width")
    if (
        not isinstance(motion_asset_public_id, str)
        or not isinstance(motion_name, str)
        or not isinstance(duration_seconds, int | float)
        or not isinstance(height, int | float)
        or not isinstance(width, int | float)
    ):
        raise LookupError("Video asset creation details are incomplete.")

    return {
        "created_at": video_asset.created_at,
        "duration_seconds": float(duration_seconds),
        "file_size_bytes": file_size_bytes,
        "height": int(height),
        "job_public_id": latest_job.public_id if latest_job is not None else None,
        "motion_asset_public_id": uuid.UUID(motion_asset_public_id),
        "motion_name": motion_name,
        "public_id": video_asset.public_id,
        "status": "available" if url is not None else video_asset.status,
        "storage_object_public_id": storage_object_public_id,
        "url": url,
        "width": int(width),
    }


def get_video_asset(session: Session, video_asset_public_id: uuid.UUID) -> Asset | None:
    return session.execute(
        _asset_query().where(
            Asset.public_id == video_asset_public_id,
            Asset.asset_type == "character-motion-video",
        )
    ).scalar_one_or_none()


def get_video_storage_object(
    session: Session,
    video_asset_public_id: uuid.UUID,
) -> StorageObject | None:
    return _video_storage_object_by_public_id(session, video_asset_public_id)


def get_video_screen_payload(
    session: Session,
    *,
    api_base_url: str,
) -> dict[str, object]:
    character_assets = list(
        session.scalars(_asset_query().where(Asset.asset_type == "character")).all()
    )

    characters: list[dict[str, object]] = []
    for character_asset in character_assets:
        latest_video_asset = _latest_video_asset(session, character_asset.id)
        latest_job = (
            _latest_video_job(session, latest_video_asset.id)
            if latest_video_asset is not None
            else None
        )
        characters.append(
            {
                "current_motion": get_character_motion_assignment(
                    session,
                    character_asset.public_id,
                ),
                "label": _character_label(session, character_asset),
                "latest_video": _latest_video_payload(
                    session,
                    api_base_url=api_base_url,
                    video_asset=latest_video_asset,
                ),
                "public_id": character_asset.public_id,
                "render_history": [
                    {
                        "created_at": event.created_at,
                        "details": event.details,
                        "event_type": event.event_type,
                        "public_id": event.public_id,
                    }
                    for event in _character_video_history(session, character_asset.id)
                ],
                "render_job": _video_job_payload(latest_job),
                "status": character_asset.status,
            }
        )

    return {
        "characters": characters,
        "render_policy": (
            "Phase 24 renders a real rig-driven Blender clip from the assigned motion clip. "
            "No AI text-to-video substitution is used here."
        ),
    }


def execute_video_render_job(
    session: Session,
    job: Job,
    payload: VideoRenderJobPayload,
) -> uuid.UUID:
    character_asset = get_character_asset(session, payload.character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")
    if job.output_asset_id is None:
        raise LookupError("Video render job has no output asset.")

    video_asset = session.get(Asset, job.output_asset_id)
    if video_asset is None or video_asset.asset_type != "character-motion-video":
        raise LookupError("Video output asset not found.")

    _run_blender_background_job(payload)

    output_path = Path(payload.output_video_path)
    if not output_path.exists():
        raise FileNotFoundError(f"Blender render did not produce '{output_path}'.")

    actor_id = get_system_actor_id(session)
    storage_object = _video_storage_object(session, video_asset.id)
    if storage_object is None:
        storage_object = StorageObject(
            storage_path=str(output_path),
            root_class=payload.render_root_class,
            object_type="character-motion-video-mp4",
            media_type="video/mp4",
            byte_size=output_path.stat().st_size,
            sha256=_sha256(output_path),
            created_by_actor_id=actor_id,
            current_owner_actor_id=actor_id,
            source_asset_id=video_asset.id,
        )
        session.add(storage_object)
        session.flush()
    else:
        storage_object.storage_path = str(output_path)
        storage_object.root_class = payload.render_root_class
        storage_object.media_type = "video/mp4"
        storage_object.byte_size = output_path.stat().st_size
        storage_object.sha256 = _sha256(output_path)
        storage_object.current_owner_actor_id = actor_id
        session.flush()

    video_asset.status = "available"
    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "duration_seconds": payload.duration_seconds,
            "height": payload.resolution_height,
            "job_public_id": str(job.public_id),
            "motion_asset_public_id": str(payload.motion_asset_public_id),
            "motion_name": payload.motion_name,
            "video_asset_public_id": str(video_asset.public_id),
            "width": payload.resolution_width,
        },
        event_type="video.render_completed",
    )
    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "job_public_id": str(job.public_id),
            "storage_object_public_id": str(storage_object.public_id),
            "storage_path": str(output_path),
            "video_asset_public_id": str(video_asset.public_id),
            "workflow_path": payload.workflow_path,
        },
        event_type="video.output_registered",
    )
    _record_history_event(
        session,
        actor_id,
        asset_id=video_asset.id,
        details={
            "job_public_id": str(job.public_id),
            "storage_object_public_id": str(storage_object.public_id),
            "storage_path": str(output_path),
            "workflow_path": payload.workflow_path,
        },
        event_type="video.output_registered",
    )
    session.flush()
    return storage_object.id


def mark_video_render_job_failed(
    session: Session,
    job: Job,
    error_summary: str,
) -> None:
    if job.output_asset_id is None:
        return

    video_asset = session.get(Asset, job.output_asset_id)
    if video_asset is None or video_asset.asset_type != "character-motion-video":
        return

    actor_id = get_system_actor_id(session)
    video_asset.status = "failed"
    if video_asset.parent_asset_id is not None:
        _record_history_event(
            session,
            actor_id,
            asset_id=video_asset.parent_asset_id,
            details={
                "error_summary": error_summary,
                "job_public_id": str(job.public_id),
                "video_asset_public_id": str(video_asset.public_id),
            },
            event_type="video.render_failed",
        )
    _record_history_event(
        session,
        actor_id,
        asset_id=video_asset.id,
        details={
            "error_summary": error_summary,
            "job_public_id": str(job.public_id),
        },
        event_type="video.render_failed",
    )
    session.flush()

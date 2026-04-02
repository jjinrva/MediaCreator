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
from app.models.photoset_entry import PhotosetEntry
from app.models.storage_object import StorageObject
from app.services.body_parameters import get_character_body_parameter_payload
from app.services.characters import get_character_asset
from app.services.jobs import (
    BlenderPreviewExportJobPayload,
    enqueue_job,
    get_system_actor_id,
)
from app.services.motion_library import get_character_motion_assignment
from app.services.photo_prep import (
    is_bucket_accepted_for_character_use,
    is_bucket_body_qualified,
    is_qc_status_accepted_for_character_use,
)
from app.services.pose_state import get_character_pose_state_payload
from app.services.storage_service import resolve_storage_layout
from app.services.texture_pipeline import ensure_character_base_texture

REPO_ROOT = Path(__file__).resolve().parents[4]
BLENDER_WORKFLOW_PATH = REPO_ROOT / "workflows" / "blender" / "rigify_proxy_export_v1.json"
BLENDER_SCRIPT_PATH = REPO_ROOT / "scripts" / "blender" / "rigify_proxy_export.py"
DEFAULT_BLENDER_BIN = Path("/opt/blender-4.5-lts/blender")


def _photoset_entry_query() -> Select[tuple[PhotosetEntry]]:
    return select(PhotosetEntry).order_by(PhotosetEntry.ordinal.asc())


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.asc())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_blender_bin() -> Path:
    configured = Path(os.getenv("MEDIACREATOR_BLENDER_BIN", str(DEFAULT_BLENDER_BIN)))
    if not configured.exists():
        raise FileNotFoundError(f"Blender 4.5 LTS is missing at '{configured}'.")
    return configured


def _resolve_export_root() -> tuple[Path, str]:
    layout = resolve_storage_layout()
    if layout.nas_available:
        layout.exports_root.mkdir(parents=True, exist_ok=True)
        return layout.exports_root, "nas"

    fallback_root = layout.scratch_root / "exports"
    fallback_root.mkdir(parents=True, exist_ok=True)
    return fallback_root, "scratch"


def _resolve_payload_root() -> Path:
    layout = resolve_storage_layout()
    payload_root = layout.scratch_root / "blender_runtime"
    payload_root.mkdir(parents=True, exist_ok=True)
    return payload_root


def _source_photoset(session: Session, character_asset: Asset) -> Asset:
    if character_asset.source_asset_id is None:
        raise LookupError("Character has no source photoset.")

    photoset_asset = session.get(Asset, character_asset.source_asset_id)
    if photoset_asset is None or photoset_asset.asset_type != "photoset":
        raise LookupError("Character source photoset not found.")
    return photoset_asset


def _input_asset_paths(session: Session, photoset_asset_id: uuid.UUID) -> list[str]:
    paths: list[str] = []
    photoset_entries = session.scalars(
        _photoset_entry_query().where(PhotosetEntry.photoset_asset_id == photoset_asset_id)
    ).all()

    for entry in photoset_entries:
        accepted_for_character_use = (
            is_bucket_accepted_for_character_use(entry.bucket)
            if entry.bucket
            else is_qc_status_accepted_for_character_use(entry.qc_status)
        )
        if not accepted_for_character_use:
            continue

        preferred_storage_object_id = entry.normalized_storage_object_id
        if (
            entry.bucket
            and is_bucket_body_qualified(entry.bucket)
            and entry.body_derivative_storage_object_id is not None
        ):
            preferred_storage_object_id = entry.body_derivative_storage_object_id

        storage_object = session.get(StorageObject, preferred_storage_object_id)
        if storage_object is None:
            raise LookupError("Prepared storage object not found for character export input.")
        paths.append(storage_object.storage_path)

    return paths


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


def build_preview_export_job_payload(
    session: Session,
    character_public_id: uuid.UUID,
) -> dict[str, object]:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    photoset_asset = _source_photoset(session, character_asset)
    export_root, export_root_class = _resolve_export_root()
    output_root = export_root / "characters" / str(character_public_id)
    output_root.mkdir(parents=True, exist_ok=True)
    texture_storage_object = ensure_character_base_texture(session, character_public_id)
    motion_assignment = get_character_motion_assignment(session, character_public_id)
    motion_duration_seconds = None
    if motion_assignment is not None:
        duration_value = motion_assignment.get("duration_seconds")
        if isinstance(duration_value, int | float):
            motion_duration_seconds = float(duration_value)

    payload = BlenderPreviewExportJobPayload(
        character_public_id=character_public_id,
        input_asset_paths=_input_asset_paths(session, photoset_asset.id),
        body_values=_current_body_values(session, character_public_id),
        pose_values=_current_pose_values(session, character_public_id),
        motion_clip_name=(
            str(motion_assignment["motion_name"])
            if motion_assignment is not None and "motion_name" in motion_assignment
            else None
        ),
        motion_duration_seconds=motion_duration_seconds,
        motion_payload_path=(
            str(motion_assignment["action_payload_path"])
            if motion_assignment is not None and "action_payload_path" in motion_assignment
            else None
        ),
        base_color_texture_path=texture_storage_object.storage_path,
        texture_fidelity="base-textured",
        output_preview_glb_path=str(output_root / "preview.glb"),
        output_final_glb_path=str(output_root / "final.glb"),
        export_root_class=export_root_class,
        workflow_path=str(BLENDER_WORKFLOW_PATH),
        script_path=str(BLENDER_SCRIPT_PATH),
    )
    return payload.model_dump(mode="json")


def queue_character_preview_export(session: Session, character_public_id: uuid.UUID) -> Job:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    actor_id = get_system_actor_id(session)
    payload = build_preview_export_job_payload(session, character_public_id)
    job = enqueue_job(
        session,
        actor_id,
        payload,
        output_asset_id=character_asset.id,
    )
    return job


def _run_blender_background_job(payload: BlenderPreviewExportJobPayload) -> None:
    blender_bin = _resolve_blender_bin()
    payload_root = _resolve_payload_root()
    payload_path = payload_root / f"{payload.character_public_id}-preview-export.json"
    payload_path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")

    command = [
        str(blender_bin),
        "--background",
        "--factory-startup",
        "--python",
        payload.script_path,
        "--",
        str(payload_path),
    ]
    subprocess.run(command, check=True, cwd=str(REPO_ROOT))


def _preview_storage_object(
    session: Session,
    character_asset_id: uuid.UUID,
) -> StorageObject | None:
    return session.execute(
        _storage_object_query().where(
            StorageObject.source_asset_id == character_asset_id,
            StorageObject.object_type == "character-preview-glb",
        )
    ).scalar_one_or_none()


def _record_export_history(
    session: Session,
    actor_id: uuid.UUID,
    *,
    asset_id: uuid.UUID,
    job_public_id: uuid.UUID,
    storage_object_public_id: uuid.UUID,
    storage_path: Path,
    workflow_path: str,
) -> None:
    session.add(
        HistoryEvent(
            actor_id=actor_id,
            asset_id=asset_id,
            event_type="export.preview_generated",
            details={
                "job_public_id": str(job_public_id),
                "storage_object_public_id": str(storage_object_public_id),
                "storage_path": str(storage_path),
                "workflow_path": workflow_path,
            },
        )
    )


def _sync_preview_storage_object(
    session: Session,
    *,
    character_asset: Asset,
    job_public_id: uuid.UUID,
    output_path: Path,
    root_class: str,
    workflow_path: str,
) -> StorageObject:
    actor_id = get_system_actor_id(session)
    storage_object = _preview_storage_object(session, character_asset.id)
    if storage_object is None:
        storage_object = StorageObject(
            storage_path=str(output_path),
            root_class=root_class,
            object_type="character-preview-glb",
            media_type="model/gltf-binary",
            byte_size=output_path.stat().st_size,
            sha256=_sha256(output_path),
            created_by_actor_id=actor_id,
            current_owner_actor_id=actor_id,
            source_asset_id=character_asset.id,
        )
        session.add(storage_object)
        session.flush()
    else:
        storage_object.storage_path = str(output_path)
        storage_object.root_class = root_class
        storage_object.media_type = "model/gltf-binary"
        storage_object.byte_size = output_path.stat().st_size
        storage_object.sha256 = _sha256(output_path)
        storage_object.current_owner_actor_id = actor_id
        session.flush()

    _record_export_history(
        session,
        actor_id,
        asset_id=character_asset.id,
        job_public_id=job_public_id,
        storage_object_public_id=storage_object.public_id,
        storage_path=output_path,
        workflow_path=workflow_path,
    )
    return storage_object


def execute_blender_preview_export_job(
    session: Session,
    job: Job,
    payload: BlenderPreviewExportJobPayload,
) -> uuid.UUID:
    character_asset = get_character_asset(session, payload.character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    _run_blender_background_job(payload)

    output_path = Path(payload.output_preview_glb_path)
    if not output_path.exists():
        raise FileNotFoundError(f"Blender export did not produce '{output_path}'.")

    storage_object = _sync_preview_storage_object(
        session,
        character_asset=character_asset,
        job_public_id=job.public_id,
        output_path=output_path,
        root_class=payload.export_root_class,
        workflow_path=payload.workflow_path,
    )
    return storage_object.id

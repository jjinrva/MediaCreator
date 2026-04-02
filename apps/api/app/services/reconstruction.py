from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history_event import HistoryEvent
from app.models.job import Job
from app.models.photoset_entry import PhotosetEntry
from app.models.storage_object import StorageObject
from app.services.blender_runtime import (
    build_preview_export_job_payload,
    execute_blender_preview_export_job,
)
from app.services.characters import get_character_asset
from app.services.jobs import (
    BlenderPreviewExportJobPayload,
    HighDetailReconstructionJobPayload,
    enqueue_job,
    get_system_actor_id,
)
from app.services.storage_service import resolve_storage_layout


@dataclass(frozen=True)
class ReconstructionAssessment:
    accepted_entry_count: int
    detail_level: str
    qualifies_for_detail_prep: bool
    reconstruction_strategy: str


def _photoset_entry_query() -> Select[tuple[PhotosetEntry]]:
    return select(PhotosetEntry).order_by(PhotosetEntry.ordinal.asc())


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.asc())


def _source_photoset(session: Session, character_asset: Asset) -> Asset:
    if character_asset.source_asset_id is None:
        raise LookupError("Character has no source photoset.")

    photoset_asset = session.get(Asset, character_asset.source_asset_id)
    if photoset_asset is None or photoset_asset.asset_type != "photoset":
        raise LookupError("Character source photoset not found.")
    return photoset_asset


def _capture_entries(session: Session, photoset_asset_id: uuid.UUID) -> list[PhotosetEntry]:
    return list(
        session.scalars(
            _photoset_entry_query().where(PhotosetEntry.photoset_asset_id == photoset_asset_id)
        ).all()
    )


def _capture_input_paths(session: Session, photoset_asset_id: uuid.UUID) -> list[str]:
    paths: list[str] = []
    for entry in _capture_entries(session, photoset_asset_id):
        storage_object = session.get(StorageObject, entry.normalized_storage_object_id)
        if storage_object is None:
            raise LookupError("Normalized storage object not found for photoset entry.")
        paths.append(storage_object.storage_path)
    return paths


def _assessment_for_entry_count(accepted_entry_count: int) -> ReconstructionAssessment:
    qualifies_for_detail_prep = accepted_entry_count >= 6
    return ReconstructionAssessment(
        accepted_entry_count=accepted_entry_count,
        detail_level=(
            "riggable-base-plus-detail-prep" if qualifies_for_detail_prep else "riggable-base-only"
        ),
        qualifies_for_detail_prep=qualifies_for_detail_prep,
        reconstruction_strategy=(
            "smplx-stage1-plus-colmap-prep" if qualifies_for_detail_prep else "smplx-stage1-only"
        ),
    )


def assess_character_capture(
    session: Session,
    character_public_id: uuid.UUID,
) -> ReconstructionAssessment:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    photoset_asset = _source_photoset(session, character_asset)
    accepted_entry_count = len(_capture_entries(session, photoset_asset.id))
    return _assessment_for_entry_count(accepted_entry_count)


def _resolve_output_root(character_public_id: uuid.UUID) -> tuple[Path, str]:
    layout = resolve_storage_layout()
    if layout.nas_available:
        export_root = layout.exports_root
        root_class = "nas"
    else:
        export_root = layout.scratch_root / "exports"
        root_class = "scratch"

    output_root = export_root / "characters" / str(character_public_id) / "reconstruction"
    output_root.mkdir(parents=True, exist_ok=True)
    return output_root, root_class


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


def _detail_prep_storage_object(
    session: Session,
    character_asset_id: uuid.UUID,
) -> StorageObject | None:
    return session.execute(
        _storage_object_query().where(
            StorageObject.source_asset_id == character_asset_id,
            StorageObject.object_type == "character-detail-prep-manifest",
        )
    ).scalar_one_or_none()


def build_reconstruction_job_payload(
    session: Session,
    character_public_id: uuid.UUID,
) -> dict[str, object]:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    photoset_asset = _source_photoset(session, character_asset)
    capture_paths = _capture_input_paths(session, photoset_asset.id)
    capture_entries = _capture_entries(session, photoset_asset.id)
    assessment = _assessment_for_entry_count(len(capture_entries))
    output_root, output_root_class = _resolve_output_root(character_public_id)

    payload = HighDetailReconstructionJobPayload(
        character_public_id=character_public_id,
        capture_entry_public_ids=[entry.public_id for entry in capture_entries],
        capture_input_paths=capture_paths,
        accepted_entry_count=assessment.accepted_entry_count,
        reconstruction_strategy=assessment.reconstruction_strategy,
        detail_level_target=assessment.detail_level,
        output_detail_prep_path=str(output_root / "detail-prep.json"),
        output_root_class=output_root_class,
    )
    return payload.model_dump(mode="json")


def queue_character_reconstruction(session: Session, character_public_id: uuid.UUID) -> Job:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    actor_id = get_system_actor_id(session)
    payload = build_reconstruction_job_payload(session, character_public_id)
    return enqueue_job(
        session,
        actor_id,
        payload,
        output_asset_id=character_asset.id,
    )


def _detail_prep_manifest(payload: HighDetailReconstructionJobPayload) -> bytes:
    manifest = {
        "artifact_kind": "detail-prep-manifest",
        "coarse_capture_gate": {
            "accepted_entry_count": payload.accepted_entry_count,
            "minimum_for_detail_prep": 6,
            "lighting_review_required": True,
            "overlap_review_required": True,
            "stable_subject_review_required": True,
        },
        "current_phase_truth": {
            "refined_detail_mesh_generated": False,
            "riggable_base_required": True,
            "strategy": payload.reconstruction_strategy,
        },
        "detail_level": payload.detail_level_target,
        "capture_entry_public_ids": [
            str(entry_public_id) for entry_public_id in payload.capture_entry_public_ids
        ],
        "capture_input_paths": payload.capture_input_paths,
        "next_stage_contract": [
            "fit the riggable SMPL-X family base first",
            (
                "run COLMAP-backed camera recovery and texture projection only on "
                "qualifying capture sets"
            ),
            "do not replace the riggable base with an uncontrolled detail mesh",
        ],
        "reconstruction_strategy": payload.reconstruction_strategy,
    }
    return json.dumps(manifest, indent=2).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def _sync_detail_prep_storage_object(
    session: Session,
    *,
    character_asset: Asset,
    job_public_id: uuid.UUID,
    payload: HighDetailReconstructionJobPayload,
) -> StorageObject:
    actor_id = get_system_actor_id(session)
    output_path = Path(payload.output_detail_prep_path)
    manifest_bytes = _detail_prep_manifest(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(manifest_bytes)

    storage_object = _detail_prep_storage_object(session, character_asset.id)
    if storage_object is None:
        storage_object = StorageObject(
            storage_path=str(output_path),
            root_class=payload.output_root_class,
            object_type="character-detail-prep-manifest",
            media_type="application/json",
            byte_size=len(manifest_bytes),
            sha256=_sha256_bytes(manifest_bytes),
            created_by_actor_id=actor_id,
            current_owner_actor_id=actor_id,
            source_asset_id=character_asset.id,
        )
        session.add(storage_object)
        session.flush()
    else:
        storage_object.storage_path = str(output_path)
        storage_object.root_class = payload.output_root_class
        storage_object.media_type = "application/json"
        storage_object.byte_size = len(manifest_bytes)
        storage_object.sha256 = _sha256_bytes(manifest_bytes)
        storage_object.current_owner_actor_id = actor_id
        session.flush()

    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "job_public_id": str(job_public_id),
            "storage_object_public_id": str(storage_object.public_id),
            "storage_path": str(output_path),
            "strategy": payload.reconstruction_strategy,
        },
        event_type="reconstruction.detail_prep_generated",
    )
    return storage_object


def execute_character_reconstruction_job(
    session: Session,
    job: Job,
    payload: HighDetailReconstructionJobPayload,
) -> uuid.UUID:
    character_asset = get_character_asset(session, payload.character_public_id)
    if character_asset is None:
        raise LookupError("Character not found.")

    preview_storage = _preview_storage_object(session, character_asset.id)
    if preview_storage is None or not Path(preview_storage.storage_path).exists():
        preview_payload = BlenderPreviewExportJobPayload.model_validate(
            build_preview_export_job_payload(session, payload.character_public_id)
        )
        preview_storage_id = execute_blender_preview_export_job(session, job, preview_payload)
        preview_storage = session.get(StorageObject, preview_storage_id)
        if preview_storage is None:
            raise LookupError("Riggable base GLB storage object was not written.")

    actor_id = get_system_actor_id(session)
    detail_storage: StorageObject | None = None
    if payload.detail_level_target == "riggable-base-plus-detail-prep":
        detail_storage = _sync_detail_prep_storage_object(
            session,
            character_asset=character_asset,
            job_public_id=job.public_id,
            payload=payload,
        )

    _record_history_event(
        session,
        actor_id,
        asset_id=character_asset.id,
        details={
            "accepted_entry_count": payload.accepted_entry_count,
            "detail_level": payload.detail_level_target,
            "job_public_id": str(job.public_id),
            "reconstruction_strategy": payload.reconstruction_strategy,
            "riggable_base_storage_object_public_id": str(preview_storage.public_id),
            "detail_prep_storage_object_public_id": (
                str(detail_storage.public_id) if detail_storage is not None else None
            ),
        },
        event_type="reconstruction.completed",
    )
    return detail_storage.id if detail_storage is not None else preview_storage.id

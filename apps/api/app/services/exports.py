from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.storage_object import StorageObject
from app.services.characters import get_character_asset


def _storage_object_query() -> Select[tuple[StorageObject]]:
    return select(StorageObject).order_by(StorageObject.created_at.asc())


def _job_query() -> Select[tuple[Job]]:
    return select(Job).order_by(Job.created_at.desc())


def _character_storage_object(
    session: Session,
    *,
    character_asset_id: uuid.UUID,
    object_type: str,
) -> StorageObject | None:
    return session.execute(
        _storage_object_query().where(
            StorageObject.source_asset_id == character_asset_id,
            StorageObject.object_type == object_type,
        )
    ).scalar_one_or_none()


def _latest_preview_export_job(session: Session, character_asset_id: uuid.UUID) -> Job | None:
    return session.execute(
        _job_query().where(
            Job.output_asset_id == character_asset_id,
            Job.job_type == "blender-preview-export",
        )
    ).scalar_one_or_none()


def _export_job_payload(job: Job | None) -> dict[str, object]:
    if job is None:
        return {
            "status": "not-queued",
            "detail": (
                "Phase 12 establishes the export destination only. No Blender export job has "
                "been queued yet."
            ),
        }

    if job.status == "completed":
        return {
            "status": job.status,
            "detail": "Latest Blender preview export job completed successfully.",
        }
    if job.status == "failed":
        return {
            "status": job.status,
            "detail": job.error_summary or "Latest Blender preview export job failed.",
        }

    return {
        "status": job.status,
        "detail": f"Latest Blender preview export job is {job.status}.",
    }


def _artifact_payload(
    *,
    api_base_url: str,
    available_detail: str,
    character_public_id: uuid.UUID,
    detail_if_missing: str,
    path_suffix: str,
    storage_object: StorageObject | None,
) -> dict[str, object]:
    if storage_object is None or not Path(storage_object.storage_path).exists():
        return {
            "status": "not-ready",
            "detail": detail_if_missing,
            "storage_object_public_id": None,
            "url": None,
        }

    return {
        "status": "available",
        "detail": available_detail,
        "storage_object_public_id": storage_object.public_id,
        "url": f"{api_base_url}/api/v1/exports/characters/{character_public_id}/{path_suffix}",
    }


def get_character_export_payload(
    session: Session,
    character_public_id: uuid.UUID,
    *,
    api_base_url: str,
) -> dict[str, object] | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None

    preview_storage = _character_storage_object(
        session,
        character_asset_id=character_asset.id,
        object_type="character-preview-glb",
    )
    final_storage = _character_storage_object(
        session,
        character_asset_id=character_asset.id,
        object_type="character-export-glb",
    )
    latest_preview_export_job = _latest_preview_export_job(session, character_asset.id)

    return {
        "character_public_id": character_asset.public_id,
        "preview_glb": _artifact_payload(
            api_base_url=api_base_url,
            available_detail="Preview GLB exported from the Blender Rigify runtime is available.",
            character_public_id=character_asset.public_id,
            detail_if_missing=(
                "No GLB preview is available yet. Later Blender export phases will write the "
                "preview artifact here."
            ),
            path_suffix="preview.glb",
            storage_object=preview_storage,
        ),
        "final_glb": _artifact_payload(
            api_base_url=api_base_url,
            available_detail="Final GLB export is available for this character.",
            character_public_id=character_asset.public_id,
            detail_if_missing=(
                "No final GLB export is available yet. Phase 12 only establishes the stable "
                "destination for later Blender export phases."
            ),
            path_suffix="final.glb",
            storage_object=final_storage,
        ),
        "export_job": _export_job_payload(latest_preview_export_job),
    }


def get_character_preview_glb_storage_object(
    session: Session,
    character_public_id: uuid.UUID,
) -> StorageObject | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None
    return _character_storage_object(
        session,
        character_asset_id=character_asset.id,
        object_type="character-preview-glb",
    )


def get_character_final_glb_storage_object(
    session: Session,
    character_public_id: uuid.UUID,
) -> StorageObject | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None
    return _character_storage_object(
        session,
        character_asset_id=character_asset.id,
        object_type="character-export-glb",
    )

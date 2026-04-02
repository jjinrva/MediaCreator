from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.storage_object import StorageObject
from app.services.characters import get_character_asset
from app.services.reconstruction import assess_character_capture
from app.services.texture_pipeline import (
    get_character_base_texture_storage_object,
    get_character_refined_texture_storage_object,
)


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


def _latest_reconstruction_job(session: Session, character_asset_id: uuid.UUID) -> Job | None:
    return session.execute(
        _job_query().where(
            Job.output_asset_id == character_asset_id,
            Job.job_type == "high-detail-reconstruction",
        )
    ).scalar_one_or_none()


def _export_job_payload(job: Job | None) -> dict[str, object]:
    if job is None:
        return {
            "job_public_id": None,
            "status": "not-queued",
            "step_name": None,
            "progress_percent": None,
            "detail": (
                "Phase 12 establishes the export destination only. No Blender export job has "
                "been queued yet."
            ),
        }

    if job.status == "completed":
        return {
            "job_public_id": job.public_id,
            "status": job.status,
            "step_name": job.step_name,
            "progress_percent": job.progress_percent,
            "detail": "Latest Blender preview export job completed successfully.",
        }
    if job.status == "failed":
        return {
            "job_public_id": job.public_id,
            "status": job.status,
            "step_name": job.step_name,
            "progress_percent": job.progress_percent,
            "detail": job.error_summary or "Latest Blender preview export job failed.",
        }

    return {
        "job_public_id": job.public_id,
        "status": job.status,
        "step_name": job.step_name,
        "progress_percent": job.progress_percent,
        "detail": f"Latest Blender preview export job is {job.status}.",
    }


def _reconstruction_job_payload(job: Job | None) -> dict[str, object]:
    if job is None:
        return {
            "job_public_id": None,
            "status": "not-queued",
            "step_name": None,
            "progress_percent": None,
            "detail": (
                "The high-detail path has not run yet. Queue it to generate a riggable base "
                "summary and evaluate whether the current capture set qualifies for detail prep."
            ),
        }

    if job.status == "completed":
        return {
            "job_public_id": job.public_id,
            "status": job.status,
            "step_name": job.step_name,
            "progress_percent": job.progress_percent,
            "detail": "Latest high-detail reconstruction job completed successfully.",
        }
    if job.status == "failed":
        return {
            "job_public_id": job.public_id,
            "status": job.status,
            "step_name": job.step_name,
            "progress_percent": job.progress_percent,
            "detail": job.error_summary or "Latest high-detail reconstruction job failed.",
        }

    return {
        "job_public_id": job.public_id,
        "status": job.status,
        "step_name": job.step_name,
        "progress_percent": job.progress_percent,
        "detail": f"Latest high-detail reconstruction job is {job.status}.",
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


def _strategy_from_job(job: Job | None, fallback: str) -> str:
    if job is None:
        return fallback
    strategy = job.payload.get("reconstruction_strategy")
    return strategy if isinstance(strategy, str) else fallback


def _detail_level(
    *,
    detail_storage: StorageObject | None,
    preview_storage: StorageObject | None,
) -> str:
    if detail_storage is not None and Path(detail_storage.storage_path).exists():
        return "riggable-base-plus-detail-prep"
    if preview_storage is not None and Path(preview_storage.storage_path).exists():
        return "riggable-base-only"
    return "not-started"


def _reconstruction_detail(
    *,
    detail_level: str,
    strategy: str,
) -> str:
    if detail_level == "riggable-base-plus-detail-prep":
        return (
            "The riggable base GLB is available and the current capture set qualified for the "
            "COLMAP-backed detail-prep contract. Phase 18 does not claim a freeform refined "
            "mesh yet."
        )
    if detail_level == "riggable-base-only":
        return (
            "The riggable base GLB is available, but the current capture set has not produced "
            "a detail-prep artifact. Add broader multi-view coverage before expecting the "
            f"'{strategy}' path to advance beyond the base stage."
        )
    return (
        "Run the high-detail path to generate the riggable base GLB and evaluate the current "
        "capture set for a detail-prep artifact."
    )


def _reconstruction_payload(
    session: Session,
    *,
    api_base_url: str,
    character_public_id: uuid.UUID,
    character_asset_id: uuid.UUID,
    preview_storage: StorageObject | None,
) -> dict[str, object]:
    assessment = assess_character_capture(session, character_public_id)
    detail_storage = _character_storage_object(
        session,
        character_asset_id=character_asset_id,
        object_type="character-detail-prep-manifest",
    )
    latest_reconstruction_job = _latest_reconstruction_job(session, character_asset_id)
    strategy = _strategy_from_job(latest_reconstruction_job, assessment.reconstruction_strategy)
    detail_level = _detail_level(detail_storage=detail_storage, preview_storage=preview_storage)

    return {
        "detail_level": detail_level,
        "detail": _reconstruction_detail(detail_level=detail_level, strategy=strategy),
        "strategy": strategy,
        "riggable_base_glb": _artifact_payload(
            api_base_url=api_base_url,
            available_detail="The riggable base GLB for the high-detail path is available.",
            character_public_id=character_public_id,
            detail_if_missing=(
                "No riggable base GLB is available yet. The high-detail path will generate it "
                "from the Blender-backed stage-one fit."
            ),
            path_suffix="preview.glb",
            storage_object=preview_storage,
        ),
        "detail_prep_artifact": _artifact_payload(
            api_base_url=api_base_url,
            available_detail=(
                "The capture set qualified for the detail-prep contract, and the prep artifact "
                "is available."
            ),
            character_public_id=character_public_id,
            detail_if_missing=(
                "No detail-prep artifact is available yet. Phase 18 only writes this artifact "
                "after a truthful capture-readiness pass."
            ),
            path_suffix="detail-prep.json",
            storage_object=detail_storage,
        ),
        "reconstruction_job": _reconstruction_job_payload(latest_reconstruction_job),
    }


def _current_texture_fidelity(
    *,
    base_texture_storage: StorageObject | None,
    refined_texture_storage: StorageObject | None,
) -> str:
    if refined_texture_storage is not None and Path(refined_texture_storage.storage_path).exists():
        return "refined-textured"
    if base_texture_storage is not None and Path(base_texture_storage.storage_path).exists():
        return "base-textured"
    return "untextured"


def _texture_material_detail(texture_fidelity: str) -> str:
    if texture_fidelity == "refined-textured":
        return "A refined texture set is available for this character."
    if texture_fidelity == "base-textured":
        return (
            "A base-color texture set derived from prepared capture photos is available and is "
            "carried into preview exports."
        )
    return "No persisted texture set is available yet."


def _texture_material_payload(
    session: Session,
    *,
    api_base_url: str,
    character_public_id: uuid.UUID,
) -> dict[str, object]:
    base_texture_storage = get_character_base_texture_storage_object(session, character_public_id)
    refined_texture_storage = get_character_refined_texture_storage_object(
        session,
        character_public_id,
    )
    texture_fidelity = _current_texture_fidelity(
        base_texture_storage=base_texture_storage,
        refined_texture_storage=refined_texture_storage,
    )

    return {
        "current_texture_fidelity": texture_fidelity,
        "detail": _texture_material_detail(texture_fidelity),
        "base_texture_artifact": _artifact_payload(
            api_base_url=api_base_url,
            available_detail="Base-color texture artifact is available for this character.",
            character_public_id=character_public_id,
            detail_if_missing=(
                "No base-color texture artifact is available yet. Generate a preview export to "
                "create the first truthful texture output."
            ),
            path_suffix="textures/base-color.png",
            storage_object=base_texture_storage,
        ),
        "refined_texture_artifact": _artifact_payload(
            api_base_url=api_base_url,
            available_detail="Refined texture artifact is available for this character.",
            character_public_id=character_public_id,
            detail_if_missing=(
                "No refined texture artifact is available yet. Phase 19 only guarantees the "
                "base-textured path."
            ),
            path_suffix="textures/refined-color.png",
            storage_object=refined_texture_storage,
        ),
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
    texture_material = _texture_material_payload(
        session,
        api_base_url=api_base_url,
        character_public_id=character_asset.public_id,
    )
    texture_fidelity = texture_material["current_texture_fidelity"]

    return {
        "character_public_id": character_asset.public_id,
        "preview_glb": _artifact_payload(
            api_base_url=api_base_url,
            available_detail=(
                "Preview GLB exported from the Blender Rigify runtime is available and now "
                f"carries the '{texture_fidelity}' material state."
            ),
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
            available_detail=(
                "Final GLB export is available for this character with the currently persisted "
                f"'{texture_fidelity}' material state."
            ),
            character_public_id=character_asset.public_id,
            detail_if_missing=(
                "No final GLB export is available yet. Phase 12 only establishes the stable "
                "destination for later Blender export phases."
            ),
            path_suffix="final.glb",
            storage_object=final_storage,
        ),
        "export_job": _export_job_payload(latest_preview_export_job),
        "reconstruction": _reconstruction_payload(
            session,
            api_base_url=api_base_url,
            character_public_id=character_asset.public_id,
            character_asset_id=character_asset.id,
            preview_storage=preview_storage,
        ),
        "texture_material": texture_material,
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


def get_character_detail_prep_storage_object(
    session: Session,
    character_public_id: uuid.UUID,
) -> StorageObject | None:
    character_asset = get_character_asset(session, character_public_id)
    if character_asset is None:
        return None
    return _character_storage_object(
        session,
        character_asset_id=character_asset.id,
        object_type="character-detail-prep-manifest",
    )

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.schemas.exports import CharacterExportScaffoldResponse
from app.services.blender_runtime import queue_character_preview_export
from app.services.exports import (
    get_character_detail_prep_storage_object,
    get_character_export_payload,
    get_character_final_glb_storage_object,
    get_character_preview_glb_storage_object,
)
from app.services.jobs import run_worker_once
from app.services.reconstruction import queue_character_reconstruction
from app.services.texture_pipeline import (
    get_character_base_texture_storage_object,
    get_character_refined_texture_storage_object,
)

router = APIRouter(prefix="/api/v1/exports", tags=["exports"])


@router.get("/characters/{character_public_id}", response_model=CharacterExportScaffoldResponse)
def get_character_exports(
    character_public_id: uuid.UUID,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> CharacterExportScaffoldResponse:
    payload = get_character_export_payload(
        db_session,
        character_public_id,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterExportScaffoldResponse.model_validate(payload)


@router.post(
    "/characters/{character_public_id}/preview",
    response_model=CharacterExportScaffoldResponse,
)
def generate_character_preview_glb(
    character_public_id: uuid.UUID,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> CharacterExportScaffoldResponse:
    try:
        with db_session.begin():
            queue_character_preview_export(db_session, character_public_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    worker_session_factory = sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        expire_on_commit=False,
    )
    worker_result = run_worker_once(worker_session_factory)
    if worker_result not in {"completed", "failed"}:
        raise HTTPException(status_code=500, detail="Unable to run the Blender preview export job.")

    db_session.expire_all()
    payload = get_character_export_payload(
        db_session,
        character_public_id,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterExportScaffoldResponse.model_validate(payload)


@router.post(
    "/characters/{character_public_id}/reconstruction",
    response_model=CharacterExportScaffoldResponse,
)
def run_character_reconstruction(
    character_public_id: uuid.UUID,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> CharacterExportScaffoldResponse:
    try:
        with db_session.begin():
            queue_character_reconstruction(db_session, character_public_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    worker_session_factory = sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        expire_on_commit=False,
    )
    worker_result = run_worker_once(worker_session_factory)
    if worker_result not in {"completed", "failed"}:
        raise HTTPException(
            status_code=500,
            detail="Unable to run the high-detail reconstruction job.",
        )

    db_session.expire_all()
    payload = get_character_export_payload(
        db_session,
        character_public_id,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterExportScaffoldResponse.model_validate(payload)


@router.get("/characters/{character_public_id}/preview.glb")
def get_character_preview_glb(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> FileResponse:
    storage_object = get_character_preview_glb_storage_object(db_session, character_public_id)
    if storage_object is None or not Path(storage_object.storage_path).exists():
        raise HTTPException(status_code=404, detail="Preview GLB not found.")
    return FileResponse(storage_object.storage_path, media_type="model/gltf-binary")


@router.get("/characters/{character_public_id}/final.glb")
def get_character_final_glb(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> FileResponse:
    storage_object = get_character_final_glb_storage_object(db_session, character_public_id)
    if storage_object is None or not Path(storage_object.storage_path).exists():
        raise HTTPException(status_code=404, detail="Final GLB export not found.")
    return FileResponse(storage_object.storage_path, media_type="model/gltf-binary")


@router.get("/characters/{character_public_id}/detail-prep.json")
def get_character_detail_prep_artifact(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> FileResponse:
    storage_object = get_character_detail_prep_storage_object(db_session, character_public_id)
    if storage_object is None or not Path(storage_object.storage_path).exists():
        raise HTTPException(status_code=404, detail="Detail-prep artifact not found.")
    return FileResponse(storage_object.storage_path, media_type="application/json")


@router.get("/characters/{character_public_id}/textures/base-color.png")
def get_character_base_color_texture(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> FileResponse:
    storage_object = get_character_base_texture_storage_object(db_session, character_public_id)
    if storage_object is None or not Path(storage_object.storage_path).exists():
        raise HTTPException(status_code=404, detail="Base-color texture artifact not found.")
    return FileResponse(storage_object.storage_path, media_type="image/png")


@router.get("/characters/{character_public_id}/textures/refined-color.png")
def get_character_refined_color_texture(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> FileResponse:
    storage_object = get_character_refined_texture_storage_object(db_session, character_public_id)
    if storage_object is None or not Path(storage_object.storage_path).exists():
        raise HTTPException(status_code=404, detail="Refined texture artifact not found.")
    return FileResponse(storage_object.storage_path, media_type="image/png")

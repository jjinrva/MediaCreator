import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.lora_dataset import CharacterLoraDatasetResponse
from app.services.lora_dataset import (
    build_character_lora_dataset,
    get_character_lora_dataset_manifest_storage_object,
    get_character_lora_dataset_payload,
)

router = APIRouter(prefix="/api/v1/lora-datasets", tags=["lora-datasets"])


@router.get("/characters/{character_public_id}", response_model=CharacterLoraDatasetResponse)
def get_character_lora_dataset(
    character_public_id: uuid.UUID,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> CharacterLoraDatasetResponse:
    payload = get_character_lora_dataset_payload(
        db_session,
        character_public_id,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterLoraDatasetResponse.model_validate(payload)


@router.post("/characters/{character_public_id}", response_model=CharacterLoraDatasetResponse)
def build_character_lora_dataset_route(
    character_public_id: uuid.UUID,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> CharacterLoraDatasetResponse:
    try:
        with db_session.begin():
            build_character_lora_dataset(db_session, character_public_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db_session.expire_all()
    payload = get_character_lora_dataset_payload(
        db_session,
        character_public_id,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterLoraDatasetResponse.model_validate(payload)


@router.get("/characters/{character_public_id}/manifest.json")
def get_character_lora_dataset_manifest(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> FileResponse:
    manifest_storage_object = get_character_lora_dataset_manifest_storage_object(
        db_session,
        character_public_id,
    )
    if manifest_storage_object is None or not Path(manifest_storage_object.storage_path).exists():
        raise HTTPException(status_code=404, detail="LoRA dataset manifest not found.")
    return FileResponse(manifest_storage_object.storage_path, media_type="application/json")

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.schemas.lora import CharacterLoraTrainingResponse
from app.services.jobs import run_worker_once
from app.services.lora_training import (
    get_character_lora_training_payload,
    queue_lora_training,
)

router = APIRouter(prefix="/api/v1/lora", tags=["lora"])


@router.get("/characters/{character_public_id}", response_model=CharacterLoraTrainingResponse)
def get_character_lora_training(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> CharacterLoraTrainingResponse:
    payload = get_character_lora_training_payload(db_session, character_public_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterLoraTrainingResponse.model_validate(payload)


@router.post("/characters/{character_public_id}", response_model=CharacterLoraTrainingResponse)
def train_character_lora(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> CharacterLoraTrainingResponse:
    try:
        with db_session.begin():
            queue_lora_training(db_session, character_public_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    worker_session_factory = sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        expire_on_commit=False,
    )
    worker_result = run_worker_once(worker_session_factory)
    if worker_result not in {"completed", "failed"}:
        raise HTTPException(status_code=500, detail="Unable to run the LoRA training job.")

    db_session.expire_all()
    payload = get_character_lora_training_payload(db_session, character_public_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterLoraTrainingResponse.model_validate(payload)

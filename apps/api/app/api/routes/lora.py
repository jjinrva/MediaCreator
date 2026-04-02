import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.jobs import QueuedJobResponse
from app.schemas.lora import CharacterLoraTrainingResponse
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


@router.post(
    "/characters/{character_public_id}",
    response_model=QueuedJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def train_character_lora(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> QueuedJobResponse:
    try:
        with db_session.begin():
            job = queue_lora_training(db_session, character_public_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return QueuedJobResponse(
        job_public_id=job.public_id,
        status=job.status,
        step_name=job.step_name,
        progress_percent=job.progress_percent,
        detail="LoRA training queued. Follow the job until it reaches a terminal state.",
    )

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.pose_state import CharacterPoseStateResponse, PoseStateUpdateRequest
from app.services.pose_state import (
    get_character_pose_state_payload,
    update_character_pose_state,
)

router = APIRouter(prefix="/api/v1/pose", tags=["pose"])


@router.get("/characters/{character_public_id}", response_model=CharacterPoseStateResponse)
def get_character_pose_state(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> CharacterPoseStateResponse:
    payload = get_character_pose_state_payload(db_session, character_public_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterPoseStateResponse.model_validate(payload)


@router.put("/characters/{character_public_id}", response_model=CharacterPoseStateResponse)
def update_pose_state(
    character_public_id: uuid.UUID,
    payload: PoseStateUpdateRequest,
    db_session: Session = Depends(get_db_session),
) -> CharacterPoseStateResponse:
    try:
        with db_session.begin():
            updated_payload = update_character_pose_state(
                db_session,
                character_public_id,
                numeric_value=payload.numeric_value,
                parameter_key=payload.parameter_key,
            )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return CharacterPoseStateResponse.model_validate(updated_payload)

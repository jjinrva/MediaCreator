import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.motion import MotionAssignmentRequest, MotionScreenResponse
from app.services.motion_library import assign_motion_to_character, get_motion_screen_payload

router = APIRouter(prefix="/api/v1/motion", tags=["motion"])


@router.get("", response_model=MotionScreenResponse)
def get_motion_screen(
    db_session: Session = Depends(get_db_session),
) -> MotionScreenResponse:
    with db_session.begin():
        payload = get_motion_screen_payload(db_session)
    return MotionScreenResponse.model_validate(payload)


@router.put("/characters/{character_public_id}", response_model=MotionScreenResponse)
def assign_character_motion(
    character_public_id: uuid.UUID,
    body: MotionAssignmentRequest,
    db_session: Session = Depends(get_db_session),
) -> MotionScreenResponse:
    try:
        with db_session.begin():
            assign_motion_to_character(
                db_session,
                character_public_id,
                body.motion_public_id,
            )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    payload = get_motion_screen_payload(db_session)
    return MotionScreenResponse.model_validate(payload)

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.body_parameters import BodyParameterUpdateRequest, CharacterBodyParameterResponse
from app.services.body_parameters import (
    get_character_body_parameter_payload,
    update_character_body_parameter,
)

router = APIRouter(prefix="/api/v1/body", tags=["body"])


@router.get("/characters/{character_public_id}", response_model=CharacterBodyParameterResponse)
def get_character_body_parameters(
    character_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> CharacterBodyParameterResponse:
    payload = get_character_body_parameter_payload(db_session, character_public_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterBodyParameterResponse.model_validate(payload)


@router.put("/characters/{character_public_id}", response_model=CharacterBodyParameterResponse)
def update_body_parameter(
    character_public_id: uuid.UUID,
    payload: BodyParameterUpdateRequest,
    db_session: Session = Depends(get_db_session),
) -> CharacterBodyParameterResponse:
    try:
        with db_session.begin():
            updated_payload = update_character_body_parameter(
                db_session,
                character_public_id,
                numeric_value=payload.numeric_value,
                parameter_key=payload.parameter_key,
            )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return CharacterBodyParameterResponse.model_validate(updated_payload)

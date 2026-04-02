import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.characters import CharacterCreateRequest, CharacterDetailResponse
from app.services.characters import create_character_from_photoset, get_character_payload

router = APIRouter(prefix="/api/v1/characters", tags=["characters"])


@router.post("", response_model=CharacterDetailResponse)
def create_character(
    payload: CharacterCreateRequest,
    request: Request,
    response: Response,
    db_session: Session = Depends(get_db_session),
) -> CharacterDetailResponse:
    try:
        with db_session.begin():
            character_asset, created = create_character_from_photoset(
                db_session,
                payload.photoset_public_id,
            )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    response.status_code = 201 if created else 200
    character_payload = get_character_payload(
        db_session,
        character_asset.public_id,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    if character_payload is None:  # pragma: no cover - guarded by the same transaction
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterDetailResponse.model_validate(character_payload)


@router.get("/{character_public_id}", response_model=CharacterDetailResponse)
def get_character_detail(
    character_public_id: uuid.UUID,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> CharacterDetailResponse:
    try:
        payload = get_character_payload(
            db_session,
            character_public_id,
            api_base_url=str(request.base_url).rstrip("/"),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if payload is None:
        raise HTTPException(status_code=404, detail="Character not found.")
    return CharacterDetailResponse.model_validate(payload)

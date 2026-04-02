import uuid
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.photosets import PhotosetDetailResponse
from app.services.photo_prep import (
    IncomingPhotoUpload,
    get_artifact_storage_object,
    get_photoset_payload,
    ingest_photoset,
)

router = APIRouter(prefix="/api/v1/photosets", tags=["photosets"])


@router.post("", response_model=PhotosetDetailResponse, status_code=201)
async def create_photoset(
    request: Request,
    photos: list[UploadFile] = File(...),
    character_label: str | None = Form(None),
    db_session: Session = Depends(get_db_session),
) -> PhotosetDetailResponse:
    uploads: list[IncomingPhotoUpload] = []

    for upload in photos:
        uploads.append(
            IncomingPhotoUpload(
                content=await upload.read(),
                filename=upload.filename or "upload",
                media_type=upload.content_type,
            )
        )

    try:
        with db_session.begin():
            photoset_asset = ingest_photoset(
                db_session,
                uploads,
                character_label=character_label,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = get_photoset_payload(
        db_session,
        photoset_asset.public_id,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    if payload is None:  # pragma: no cover - guarded by same transaction above
        raise HTTPException(status_code=404, detail="Photoset not found.")
    return PhotosetDetailResponse.model_validate(payload)


@router.get("/{photoset_public_id}", response_model=PhotosetDetailResponse)
def get_photoset_detail(
    photoset_public_id: uuid.UUID,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> PhotosetDetailResponse:
    payload = get_photoset_payload(
        db_session,
        photoset_public_id,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Photoset not found.")
    return PhotosetDetailResponse.model_validate(payload)


@router.get("/{photoset_public_id}/entries/{entry_public_id}/artifacts/{variant}")
def get_photoset_artifact(
    photoset_public_id: uuid.UUID,
    entry_public_id: uuid.UUID,
    variant: Literal["original", "normalized", "thumbnail"],
    db_session: Session = Depends(get_db_session),
) -> FileResponse:
    storage_object = get_artifact_storage_object(
        db_session,
        photoset_public_id,
        entry_public_id,
        variant,
    )
    if storage_object is None:
        raise HTTPException(status_code=404, detail="Artifact not found.")

    return FileResponse(storage_object.storage_path, media_type=storage_object.media_type)

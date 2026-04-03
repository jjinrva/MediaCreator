import shutil
import uuid
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.photosets import PhotosetDetailResponse
from app.services import photo_prep
from app.services.photo_prep import (
    IncomingPhotoUpload,
    get_artifact_storage_object,
    get_photoset_payload,
    ingest_photoset,
)

router = APIRouter(prefix="/api/v1/photosets", tags=["photosets"])


async def _stage_upload(upload: UploadFile, staged_root: Path) -> IncomingPhotoUpload:
    filename = upload.filename or "upload"
    media_type = photo_prep.resolve_upload_media_type(filename, upload.content_type)
    if media_type not in photo_prep.ALLOWED_IMAGE_MEDIA_TYPES:
        raise ValueError(f"Unsupported media type for '{filename}': {media_type}")

    staged_path = staged_root / (
        f"{uuid.uuid4()}{photo_prep.extension_for_upload_filename(filename, media_type)}"
    )
    byte_size = 0

    try:
        with staged_path.open("wb") as staged_file:
            while True:
                chunk = await upload.read(photo_prep.UPLOAD_WRITE_CHUNK_SIZE_BYTES)
                if not chunk:
                    break
                byte_size += len(chunk)
                if byte_size > photo_prep.MAX_UPLOAD_FILE_SIZE_BYTES:
                    raise ValueError(
                        "File "
                        f"'{filename}' exceeds the {photo_prep.MAX_UPLOAD_FILE_SIZE_BYTES} byte "
                        "upload limit."
                    )
                staged_file.write(chunk)
    except Exception:
        staged_path.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    if byte_size <= 0:
        staged_path.unlink(missing_ok=True)
        raise ValueError(f"Uploaded file '{filename}' is empty.")

    return IncomingPhotoUpload(
        byte_size=byte_size,
        filename=filename,
        media_type=media_type,
        staged_path=staged_path,
    )


@router.post("", response_model=PhotosetDetailResponse, status_code=202)
async def create_photoset(
    request: Request,
    photos: list[UploadFile] = File(...),
    character_label: str | None = Form(None),
    db_session: Session = Depends(get_db_session),
) -> PhotosetDetailResponse:
    if len(photos) > photo_prep.MAX_UPLOAD_FILE_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"A photoset may contain at most {photo_prep.MAX_UPLOAD_FILE_COUNT} files.",
        )

    uploads: list[IncomingPhotoUpload] = []
    staged_root = photo_prep.create_upload_staging_root()
    keep_staged_uploads = False

    try:
        for upload in photos:
            uploads.append(await _stage_upload(upload, staged_root))
        with db_session.begin():
            ingest_result = ingest_photoset(
                db_session,
                uploads,
                character_label=character_label,
            )
        keep_staged_uploads = True
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if not keep_staged_uploads:
            shutil.rmtree(staged_root, ignore_errors=True)

    payload = get_photoset_payload(
        db_session,
        ingest_result.photoset_asset.public_id,
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
    variant: Literal["body", "lora", "original", "normalized", "thumbnail"],
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

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.wardrobe import CreateWardrobeFromPromptRequest, WardrobeCatalogResponse
from app.services.wardrobe import (
    IncomingWardrobePhotoUpload,
    create_wardrobe_from_photo,
    create_wardrobe_from_prompt,
    get_wardrobe_catalog_payload,
    get_wardrobe_source_photo_storage_object,
)

router = APIRouter(prefix="/api/v1/wardrobe", tags=["wardrobe"])


@router.get("", response_model=WardrobeCatalogResponse)
def get_wardrobe_catalog(
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> WardrobeCatalogResponse:
    payload = get_wardrobe_catalog_payload(
        db_session,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    return WardrobeCatalogResponse.model_validate(payload)


@router.post("/from-photo", response_model=WardrobeCatalogResponse, status_code=201)
async def create_wardrobe_item_from_photo(
    request: Request,
    photo: UploadFile = File(...),
    label: str = Form(...),
    garment_type: str = Form(...),
    material: str = Form(...),
    base_color: str = Form(...),
    db_session: Session = Depends(get_db_session),
) -> WardrobeCatalogResponse:
    upload = IncomingWardrobePhotoUpload(
        content=await photo.read(),
        filename=photo.filename or "wardrobe-source.png",
        media_type=photo.content_type,
    )

    try:
        with db_session.begin():
            create_wardrobe_from_photo(
                db_session,
                upload,
                base_color=base_color,
                garment_type=garment_type,
                label=label,
                material_label=material,
            )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = get_wardrobe_catalog_payload(
        db_session,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    return WardrobeCatalogResponse.model_validate(payload)


@router.post("/from-prompt", response_model=WardrobeCatalogResponse, status_code=201)
def create_wardrobe_item_from_prompt(
    request: Request,
    body: CreateWardrobeFromPromptRequest,
    db_session: Session = Depends(get_db_session),
) -> WardrobeCatalogResponse:
    try:
        with db_session.begin():
            create_wardrobe_from_prompt(
                db_session,
                base_color=body.base_color,
                garment_type=body.garment_type,
                label=body.label,
                material_label=body.material,
                prompt_text=body.prompt_text,
            )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = get_wardrobe_catalog_payload(
        db_session,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    return WardrobeCatalogResponse.model_validate(payload)


@router.get("/{wardrobe_public_id}/source-photo")
def get_wardrobe_source_photo(
    wardrobe_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> FileResponse:
    storage_object = get_wardrobe_source_photo_storage_object(db_session, wardrobe_public_id)
    if storage_object is None:
        raise HTTPException(status_code=404, detail="Wardrobe source photo not found.")
    return FileResponse(storage_object.storage_path, media_type=storage_object.media_type)

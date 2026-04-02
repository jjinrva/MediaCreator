import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.schemas.video import VideoRenderRequest, VideoScreenResponse
from app.services.jobs import run_worker_once
from app.services.video_render import (
    get_video_screen_payload,
    get_video_storage_object,
    queue_character_video_render,
)

router = APIRouter(prefix="/api/v1/video", tags=["video"])


@router.get("", response_model=VideoScreenResponse)
def get_video_screen(
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> VideoScreenResponse:
    payload = get_video_screen_payload(
        db_session,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    return VideoScreenResponse.model_validate(payload)


@router.post("/characters/{character_public_id}/render", response_model=VideoScreenResponse)
def render_character_video(
    character_public_id: uuid.UUID,
    body: VideoRenderRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> VideoScreenResponse:
    try:
        with db_session.begin():
            queue_character_video_render(
                db_session,
                character_public_id,
                duration_seconds=body.duration_seconds,
                height=body.height,
                width=body.width,
            )
    except LookupError as exc:
        detail = str(exc)
        status_code = status.HTTP_409_CONFLICT if "assigned motion clip" in detail else 404
        raise HTTPException(status_code=status_code, detail=detail) from exc

    worker_session_factory = sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        expire_on_commit=False,
    )
    worker_result = run_worker_once(worker_session_factory)
    if worker_result not in {"completed", "failed"}:
        raise HTTPException(
            status_code=500,
            detail="Unable to run the controlled video render job.",
        )

    db_session.expire_all()
    payload = get_video_screen_payload(
        db_session,
        api_base_url=str(request.base_url).rstrip("/"),
    )
    return VideoScreenResponse.model_validate(payload)


@router.get("/assets/{video_asset_public_id}.mp4")
def get_rendered_video(
    video_asset_public_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
) -> FileResponse:
    storage_object = get_video_storage_object(db_session, video_asset_public_id)
    if storage_object is None or not Path(storage_object.storage_path).exists():
        raise HTTPException(status_code=404, detail="Rendered video not found.")
    return FileResponse(storage_object.storage_path, media_type="video/mp4")

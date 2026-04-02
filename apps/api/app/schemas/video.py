import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.motion import MotionAssignmentResponse


class VideoRenderHistoryEventResponse(BaseModel):
    created_at: datetime
    details: dict[str, object]
    event_type: str
    public_id: uuid.UUID


class VideoRenderJobResponse(BaseModel):
    detail: str
    public_id: uuid.UUID | None
    status: str


class VideoRenderOutputResponse(BaseModel):
    created_at: datetime
    duration_seconds: float
    file_size_bytes: int | None
    height: int
    job_public_id: uuid.UUID | None
    motion_asset_public_id: uuid.UUID
    motion_name: str
    public_id: uuid.UUID
    status: str
    storage_object_public_id: uuid.UUID | None
    url: str | None
    width: int


class VideoCharacterResponse(BaseModel):
    current_motion: MotionAssignmentResponse | None
    label: str
    latest_video: VideoRenderOutputResponse | None
    public_id: uuid.UUID
    render_history: list[VideoRenderHistoryEventResponse]
    render_job: VideoRenderJobResponse
    status: str


class VideoScreenResponse(BaseModel):
    characters: list[VideoCharacterResponse]
    render_policy: str


class VideoRenderRequest(BaseModel):
    duration_seconds: float | None = Field(default=None, ge=0.5, le=5.0)
    height: int = Field(default=480, ge=256, le=1080)
    width: int = Field(default=480, ge=256, le=1080)

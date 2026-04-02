import uuid

from pydantic import BaseModel


class MotionAssignmentResponse(BaseModel):
    action_payload_path: str
    compatible_rig_class: str
    duration_seconds: float
    motion_asset_public_id: uuid.UUID
    motion_name: str
    motion_slug: str
    source: str


class MotionClipResponse(BaseModel):
    action_payload_path: str
    compatible_rig_class: str
    duration_seconds: float
    external_import_note: str
    name: str
    public_id: uuid.UUID
    recommended_external_source: str
    slug: str
    source: str


class MotionCharacterResponse(BaseModel):
    current_motion: MotionAssignmentResponse | None
    label: str
    public_id: uuid.UUID
    status: str


class MotionScreenResponse(BaseModel):
    characters: list[MotionCharacterResponse]
    import_note: str
    motion_library: list[MotionClipResponse]


class MotionAssignmentRequest(BaseModel):
    motion_public_id: uuid.UUID

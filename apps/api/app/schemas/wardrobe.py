import uuid
from datetime import datetime

from pydantic import BaseModel


class WardrobeGenerationCapabilityResponse(BaseModel):
    detail: str
    missing_requirements: list[str]
    status: str


class WardrobeHistoryEventResponse(BaseModel):
    created_at: datetime
    details: dict[str, object]
    event_type: str
    public_id: uuid.UUID


class WardrobeItemResponse(BaseModel):
    base_color: str
    creation_path: str
    fitting_status: str
    garment_type: str
    history: list[WardrobeHistoryEventResponse]
    label: str
    material: str
    prompt_text: str | None
    public_id: uuid.UUID
    source_photo_url: str | None
    status: str


class WardrobeCatalogResponse(BaseModel):
    generation_capability: WardrobeGenerationCapabilityResponse
    items: list[WardrobeItemResponse]


class CreateWardrobeFromPromptRequest(BaseModel):
    base_color: str
    garment_type: str
    label: str
    material: str
    prompt_text: str

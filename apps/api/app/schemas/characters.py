import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.photosets import PhotosetEntryArtifactUrls


class CharacterAcceptedEntryResponse(BaseModel):
    public_id: uuid.UUID
    photo_asset_public_id: uuid.UUID
    original_filename: str
    qc_status: str
    framing_label: str
    artifact_urls: PhotosetEntryArtifactUrls


class CharacterHistoryEventResponse(BaseModel):
    public_id: uuid.UUID
    event_type: str
    created_at: datetime
    details: dict[str, object]


class CharacterCreateRequest(BaseModel):
    photoset_public_id: uuid.UUID


class CharacterDetailResponse(BaseModel):
    public_id: uuid.UUID
    asset_type: str
    status: str
    created_at: datetime
    label: str | None
    originating_photoset_public_id: uuid.UUID
    accepted_entry_count: int
    accepted_entries: list[CharacterAcceptedEntryResponse]
    history: list[CharacterHistoryEventResponse]

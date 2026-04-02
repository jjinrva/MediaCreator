import uuid

from pydantic import BaseModel


class PhotosetEntryArtifactUrls(BaseModel):
    original: str
    normalized: str
    thumbnail: str


class PhotosetQcMetrics(BaseModel):
    face_detected: bool
    body_landmarks_detected: bool
    blur_score: float
    exposure_score: float
    framing_label: str


class PhotosetEntryResponse(BaseModel):
    public_id: uuid.UUID
    photo_asset_public_id: uuid.UUID
    original_filename: str
    qc_status: str
    qc_reasons: list[str]
    qc_metrics: PhotosetQcMetrics
    original_storage_object_public_id: uuid.UUID
    normalized_storage_object_public_id: uuid.UUID
    thumbnail_storage_object_public_id: uuid.UUID
    artifact_urls: PhotosetEntryArtifactUrls


class PhotosetDetailResponse(BaseModel):
    public_id: uuid.UUID
    asset_type: str
    status: str
    entry_count: int
    entries: list[PhotosetEntryResponse]

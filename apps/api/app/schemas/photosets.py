import uuid

from pydantic import BaseModel


class PhotosetBucketCounts(BaseModel):
    lora_only: int
    body_only: int
    both: int
    rejected: int


class PhotosetEntryArtifactUrls(BaseModel):
    body: str | None = None
    lora: str | None = None
    original: str
    normalized: str
    thumbnail: str


class PhotosetQcMetrics(BaseModel):
    has_person: bool
    face_detected: bool
    body_detected: bool
    body_landmarks_detected: bool
    blur_score: float
    exposure_score: float
    framing_label: str
    occlusion_label: str
    resolution_ok: bool


class PhotosetIngestJobResponse(BaseModel):
    job_public_id: uuid.UUID
    status: str
    step_name: str | None
    progress_percent: int
    total_files: int | None = None
    processed_files: int | None = None
    bucket_counts: PhotosetBucketCounts | None = None


class PhotosetEntryResponse(BaseModel):
    accepted_for_character_use: bool
    public_id: uuid.UUID
    photo_asset_public_id: uuid.UUID
    original_filename: str
    bucket: str
    qc_status: str
    qc_reasons: list[str]
    reason_codes: list[str]
    reason_messages: list[str]
    qc_metrics: PhotosetQcMetrics
    usable_for_lora: bool
    usable_for_body: bool
    original_storage_object_public_id: uuid.UUID
    normalized_storage_object_public_id: uuid.UUID
    thumbnail_storage_object_public_id: uuid.UUID
    body_derivative_storage_object_public_id: uuid.UUID | None = None
    lora_derivative_storage_object_public_id: uuid.UUID | None = None
    artifact_urls: PhotosetEntryArtifactUrls


class PhotosetDetailResponse(BaseModel):
    accepted_entry_count: int
    public_id: uuid.UUID
    asset_type: str
    character_label: str | None = None
    status: str
    entry_count: int
    rejected_entry_count: int
    bucket_counts: PhotosetBucketCounts
    ingest_job: PhotosetIngestJobResponse | None = None
    entries: list[PhotosetEntryResponse]

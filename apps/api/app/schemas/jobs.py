import uuid
from datetime import datetime

from pydantic import BaseModel


class JobSummaryResponse(BaseModel):
    job_public_id: uuid.UUID | None
    status: str
    step_name: str | None
    progress_percent: int | None
    detail: str


class QueuedJobResponse(BaseModel):
    job_public_id: uuid.UUID
    status: str
    step_name: str | None
    progress_percent: int
    detail: str


class JobProgressResponse(BaseModel):
    total_files: int | None = None
    processed_files: int | None = None
    bucket_counts: dict[str, int] | None = None


class JobStageHistoryResponse(BaseModel):
    created_at: datetime
    event_type: str
    status: str | None = None
    step_name: str | None = None
    progress_percent: int | None = None
    total_files: int | None = None
    processed_files: int | None = None
    bucket_counts: dict[str, int] | None = None


class JobDetailResponse(BaseModel):
    public_id: uuid.UUID
    job_type: str
    status: str
    progress_percent: int
    step_name: str | None
    error_summary: str | None
    started_at: datetime | None
    finished_at: datetime | None
    output_asset_id: uuid.UUID | None
    output_storage_object_id: uuid.UUID | None
    progress: JobProgressResponse | None = None
    stage_history: list[JobStageHistoryResponse] = []

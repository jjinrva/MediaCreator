import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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

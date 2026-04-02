import uuid

from pydantic import BaseModel

from app.schemas.jobs import JobSummaryResponse


class LoraTrainingCapabilityResponse(BaseModel):
    ai_toolkit_bin: str | None
    detail: str
    loras_root: str
    missing_requirements: list[str]
    status: str


class LoraRegistryEntryResponse(BaseModel):
    details: dict[str, object]
    model_name: str
    prompt_handle: str
    public_id: uuid.UUID
    status: str
    storage_object_public_id: uuid.UUID | None


class ActiveLoraArtifactResponse(BaseModel):
    model_name: str
    prompt_handle: str
    status: str
    storage_object_public_id: uuid.UUID
    storage_path: str


class CharacterLoraTrainingResponse(BaseModel):
    character_public_id: uuid.UUID
    capability: LoraTrainingCapabilityResponse
    training_job: JobSummaryResponse
    active_model: ActiveLoraArtifactResponse | None
    registry: list[LoraRegistryEntryResponse]

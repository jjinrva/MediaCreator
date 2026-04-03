import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GenerationCapabilitySummaryResponse(BaseModel):
    detail: str
    missing_requirements: list[str]
    status: str


class CivitaiImportCapabilityResponse(BaseModel):
    base_url: str
    detail: str
    missing_requirements: list[str]
    status: str


class CharacterPromptRecipeResponse(BaseModel):
    label: str
    prompt_expansion: str
    prompt_handle: str
    public_id: uuid.UUID
    status: str
    training_prompt_status: str
    visible_tags: list[str]


class GenerationModelReferenceResponse(BaseModel):
    character_public_id: uuid.UUID | None
    model_name: str
    owner_label: str
    prompt_handle: str
    registry_public_id: uuid.UUID
    source: str
    status: str
    storage_path: str | None
    toolkit_name: str | None


class GenerationProofImageJobResponse(BaseModel):
    detail: str
    job_public_id: uuid.UUID | None
    progress_percent: int | None
    status: str
    step_name: str | None


class GenerationProofImageArtifactResponse(BaseModel):
    byte_size: int | None
    media_type: str | None
    proof_asset_public_id: uuid.UUID
    status: str
    storage_object_public_id: uuid.UUID
    url: str | None


class GenerationRequestRecordResponse(BaseModel):
    character_public_id: uuid.UUID | None
    created_at: datetime
    expanded_prompt: str
    external_lora: GenerationModelReferenceResponse | None
    local_lora: GenerationModelReferenceResponse | None
    matched_handles: list[str]
    provider_status: str
    public_id: uuid.UUID
    proof_image_artifact: GenerationProofImageArtifactResponse | None
    proof_image_job: GenerationProofImageJobResponse
    raw_prompt: str
    status: str
    target_kind: str
    workflow_id: str
    workflow_path: str


class GenerationWorkflowContractResponse(BaseModel):
    path: str
    target_kind: str
    workflow_id: str


class GenerationWorkspaceResponse(BaseModel):
    characters: list[CharacterPromptRecipeResponse]
    civitai_import: CivitaiImportCapabilityResponse
    external_loras: list[GenerationModelReferenceResponse]
    generation_capability: GenerationCapabilitySummaryResponse
    local_loras: list[GenerationModelReferenceResponse]
    recent_requests: list[GenerationRequestRecordResponse]
    workflow_contracts: list[GenerationWorkflowContractResponse]


class PromptExpansionRequest(BaseModel):
    prompt_text: str = Field(min_length=1)


class PromptExpansionResponse(BaseModel):
    expanded_prompt: str
    matched_handles: list[str]
    unresolved_handles: list[str]


class CreateGenerationRequestRequest(BaseModel):
    external_lora_registry_public_id: uuid.UUID | None = None
    local_lora_registry_public_id: uuid.UUID | None = None
    prompt_text: str = Field(min_length=1)
    target_kind: Literal["image", "video"] = "image"


class ExternalLoraSearchResponse(BaseModel):
    results: list[dict[str, str]]
    status: str


class ImportExternalLoraRequest(BaseModel):
    download_url: str
    model_name: str
    prompt_handle: str

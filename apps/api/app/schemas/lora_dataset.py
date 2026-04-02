import uuid

from pydantic import BaseModel


class CharacterLoraDatasetDetailsResponse(BaseModel):
    dataset_version: str
    detail: str
    entry_count: int
    manifest_storage_object_public_id: uuid.UUID | None
    manifest_url: str | None
    prompt_contract_version: str
    prompt_expansion: str
    prompt_handle: str
    status: str
    visible_tags: list[str]


class CharacterLoraDatasetResponse(BaseModel):
    character_public_id: uuid.UUID
    dataset: CharacterLoraDatasetDetailsResponse

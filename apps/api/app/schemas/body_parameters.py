import uuid

from pydantic import BaseModel


class BodyParameterCatalogEntryResponse(BaseModel):
    key: str
    display_label: str
    group: str
    min_value: float
    max_value: float
    step: float
    unit: str
    default_value: float
    help_text: str


class CharacterBodyParameterResponse(BaseModel):
    character_public_id: uuid.UUID
    catalog: list[BodyParameterCatalogEntryResponse]
    current_values: dict[str, float]


class BodyParameterUpdateRequest(BaseModel):
    parameter_key: str
    numeric_value: float

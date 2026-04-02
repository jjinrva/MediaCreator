import uuid

from pydantic import BaseModel


class FacialParameterCatalogEntryResponse(BaseModel):
    key: str
    display_label: str
    group: str
    shape_key_name: str
    min_value: float
    max_value: float
    step: float
    unit: str
    default_value: float
    help_text: str


class CharacterFacialParameterResponse(BaseModel):
    character_public_id: uuid.UUID
    catalog: list[FacialParameterCatalogEntryResponse]
    current_values: dict[str, float]


class FacialParameterUpdateRequest(BaseModel):
    parameter_key: str
    numeric_value: float

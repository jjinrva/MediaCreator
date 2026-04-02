import uuid

from pydantic import BaseModel


class PoseParameterCatalogEntryResponse(BaseModel):
    key: str
    display_label: str
    group: str
    bone_name: str
    axis: str
    min_value: float
    max_value: float
    step: float
    unit: str
    default_value: float
    help_text: str


class CharacterPoseStateResponse(BaseModel):
    character_public_id: uuid.UUID
    catalog: list[PoseParameterCatalogEntryResponse]
    current_values: dict[str, float]


class PoseStateUpdateRequest(BaseModel):
    parameter_key: str
    numeric_value: float

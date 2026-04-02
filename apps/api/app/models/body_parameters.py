from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDIdentityMixin


@dataclass(frozen=True)
class BodyParameterDefinition:
    key: str
    display_label: str
    group: str
    min_value: float
    max_value: float
    step: float
    unit: str
    default_value: float
    help_text: str


BODY_PARAMETER_CATALOG: tuple[BodyParameterDefinition, ...] = (
    BodyParameterDefinition(
        key="height_scale",
        display_label="Height scale",
        group="overall",
        min_value=0.85,
        max_value=1.15,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text=(
            "Scales the overall vertical body proportion that later maps to the "
            "Blender base height control."
        ),
    ),
    BodyParameterDefinition(
        key="shoulder_width",
        display_label="Shoulder width",
        group="torso",
        min_value=0.8,
        max_value=1.2,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text=(
            "Controls the width of the shoulder span and later maps to the "
            "upper-torso width target."
        ),
    ),
    BodyParameterDefinition(
        key="chest_volume",
        display_label="Chest volume",
        group="torso",
        min_value=0.75,
        max_value=1.25,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text=(
            "Controls the forward chest volume that later maps to the torso "
            "fullness shape-key group."
        ),
    ),
    BodyParameterDefinition(
        key="waist_width",
        display_label="Waist width",
        group="torso",
        min_value=0.75,
        max_value=1.25,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text=(
            "Controls waist narrowing versus widening before later natural-language "
            "mappings are added."
        ),
    ),
    BodyParameterDefinition(
        key="hip_width",
        display_label="Hip width",
        group="torso",
        min_value=0.75,
        max_value=1.25,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text=(
            "Controls the lower torso and hip breadth that later maps to "
            "pelvis-adjacent shape-key targets."
        ),
    ),
    BodyParameterDefinition(
        key="upper_arm_volume",
        display_label="Upper-arm volume",
        group="arms",
        min_value=0.75,
        max_value=1.25,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text=(
            "Controls the bicep and tricep fullness envelope for later "
            "arm-volume shape-key mapping."
        ),
    ),
    BodyParameterDefinition(
        key="thigh_volume",
        display_label="Thigh volume",
        group="legs",
        min_value=0.75,
        max_value=1.25,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text=(
            "Controls upper-leg fullness and is reserved for later thigh "
            "shape-key mapping in Blender."
        ),
    ),
    BodyParameterDefinition(
        key="calf_volume",
        display_label="Calf volume",
        group="legs",
        min_value=0.75,
        max_value=1.25,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text="Controls lower-leg fullness and later maps to the calf deformation target set.",
    ),
)


class BodyParameter(UUIDIdentityMixin, TimestampMixin, Base):
    __tablename__ = "body_parameters"
    __table_args__ = (
        UniqueConstraint(
            "character_asset_id",
            "parameter_key",
            name="uq_body_parameters_character_asset_id_parameter_key",
        ),
    )

    character_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    parameter_key: Mapped[str] = mapped_column(String(100), nullable=False)
    numeric_value: Mapped[float] = mapped_column(Float, nullable=False)

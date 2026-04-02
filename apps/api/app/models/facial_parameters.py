from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDIdentityMixin


@dataclass(frozen=True)
class FacialParameterDefinition:
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


FACIAL_PARAMETER_CATALOG: tuple[FacialParameterDefinition, ...] = (
    FacialParameterDefinition(
        key="jaw_open",
        display_label="Jaw open",
        group="mouth",
        shape_key_name="JawOpen",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        unit="x",
        default_value=0.0,
        help_text=(
            "Controls jaw opening intensity and later maps to the Blender "
            "jaw-open shape key."
        ),
    ),
    FacialParameterDefinition(
        key="smile_left",
        display_label="Smile left",
        group="mouth",
        shape_key_name="SmileLeft",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        unit="x",
        default_value=0.0,
        help_text=(
            "Controls left-side smile intensity for later Blender left-smile "
            "shape-key mapping."
        ),
    ),
    FacialParameterDefinition(
        key="smile_right",
        display_label="Smile right",
        group="mouth",
        shape_key_name="SmileRight",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        unit="x",
        default_value=0.0,
        help_text=(
            "Controls right-side smile intensity for later Blender right-smile "
            "shape-key mapping."
        ),
    ),
    FacialParameterDefinition(
        key="brow_raise",
        display_label="Brow raise",
        group="brows",
        shape_key_name="BrowRaise",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        unit="x",
        default_value=0.0,
        help_text=(
            "Controls the symmetric brow-lift factor before later corrective "
            "rig refinement."
        ),
    ),
    FacialParameterDefinition(
        key="eye_openness",
        display_label="Eye openness",
        group="eyes",
        shape_key_name="EyeOpen",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text=(
            "Controls the shared eye-open factor for later eyelid shape-key "
            "or corrective-rig mapping."
        ),
    ),
    FacialParameterDefinition(
        key="neutral_expression_blend",
        display_label="Neutral blend",
        group="base",
        shape_key_name="NeutralExpression",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        unit="x",
        default_value=1.0,
        help_text=(
            "Preserves the neutral-expression baseline that later blends with "
            "other facial controls."
        ),
    ),
)


class FacialParameter(UUIDIdentityMixin, TimestampMixin, Base):
    __tablename__ = "facial_parameters"
    __table_args__ = (
        UniqueConstraint(
            "character_asset_id",
            "parameter_key",
            name="uq_facial_parameters_character_asset_id_parameter_key",
        ),
    )

    character_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    parameter_key: Mapped[str] = mapped_column(String(100), nullable=False)
    numeric_value: Mapped[float] = mapped_column(Float, nullable=False)

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDIdentityMixin


@dataclass(frozen=True)
class PoseParameterDefinition:
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


POSE_PARAMETER_CATALOG: tuple[PoseParameterDefinition, ...] = (
    PoseParameterDefinition(
        key="upper_arm_l_pitch_deg",
        display_label="Left arm raise",
        group="arms",
        bone_name="upper_arm.L",
        axis="x",
        min_value=-45,
        max_value=90,
        step=1,
        unit="deg",
        default_value=0,
        help_text=(
            "Raises or lowers the left upper arm around the pitch axis for later rig mapping."
        ),
    ),
    PoseParameterDefinition(
        key="upper_arm_r_pitch_deg",
        display_label="Right arm raise",
        group="arms",
        bone_name="upper_arm.R",
        axis="x",
        min_value=-45,
        max_value=90,
        step=1,
        unit="deg",
        default_value=0,
        help_text=(
            "Raises or lowers the right upper arm around the pitch axis for later rig mapping."
        ),
    ),
    PoseParameterDefinition(
        key="thigh_l_pitch_deg",
        display_label="Left leg raise",
        group="legs",
        bone_name="thigh.L",
        axis="x",
        min_value=-35,
        max_value=75,
        step=1,
        unit="deg",
        default_value=0,
        help_text=(
            "Raises or lowers the left thigh around the pitch axis for later pose-bone mapping."
        ),
    ),
    PoseParameterDefinition(
        key="thigh_r_pitch_deg",
        display_label="Right leg raise",
        group="legs",
        bone_name="thigh.R",
        axis="x",
        min_value=-35,
        max_value=75,
        step=1,
        unit="deg",
        default_value=0,
        help_text=(
            "Raises or lowers the right thigh around the pitch axis for later pose-bone mapping."
        ),
    ),
)


class PoseState(UUIDIdentityMixin, TimestampMixin, Base):
    __tablename__ = "pose_state"
    __table_args__ = (
        UniqueConstraint(
            "character_asset_id",
            "parameter_key",
            name="uq_pose_state_character_asset_id_parameter_key",
        ),
    )

    character_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    parameter_key: Mapped[str] = mapped_column(String(100), nullable=False)
    numeric_value: Mapped[float] = mapped_column(Float, nullable=False)

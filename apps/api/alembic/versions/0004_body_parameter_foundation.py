"""body parameter foundation

Revision ID: 0004_body_parameter_foundation
Revises: 0003_photosets_and_qc_foundation
Create Date: 2026-04-02 12:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0004_body_parameter_foundation"
down_revision = "0003_photosets_and_qc_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "body_parameters",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "public_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "character_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("parameter_key", sa.String(length=100), nullable=False),
        sa.Column("numeric_value", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "character_asset_id",
            "parameter_key",
            name="uq_body_parameters_character_asset_id_parameter_key",
        ),
    )


def downgrade() -> None:
    op.drop_table("body_parameters")

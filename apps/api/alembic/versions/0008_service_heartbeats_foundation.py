"""service heartbeats foundation

Revision ID: 0008_service_heartbeats
Revises: 0007_model_registry_foundation
Create Date: 2026-04-02 19:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0008_service_heartbeats"
down_revision = "0007_model_registry_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_heartbeats",
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
        sa.Column("service_name", sa.String(length=100), nullable=False, unique=True),
        sa.Column(
            "detail",
            sa.String(length=255),
            nullable=False,
            server_default=sa.text("'polling'"),
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
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
    )


def downgrade() -> None:
    op.drop_table("service_heartbeats")

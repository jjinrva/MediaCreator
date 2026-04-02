"""photoset ingest truth and buckets

Revision ID: 0009_ingest_truth_buckets
Revises: 0008_service_heartbeats_foundation
Create Date: 2026-04-02 22:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0009_ingest_truth_buckets"
down_revision = "0008_service_heartbeats"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "photoset_entries",
        sa.Column(
            "bucket",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'rejected'"),
        ),
    )
    op.add_column(
        "photoset_entries",
        sa.Column(
            "usable_for_lora",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "photoset_entries",
        sa.Column(
            "usable_for_body",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "photoset_entries",
        sa.Column(
            "reason_codes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "photoset_entries",
        sa.Column(
            "reason_messages",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.execute(
        """
        UPDATE photoset_entries
        SET
            bucket = CASE
                WHEN qc_status IN ('pass', 'warn') THEN 'both'
                ELSE 'rejected'
            END,
            usable_for_lora = CASE
                WHEN qc_status IN ('pass', 'warn') THEN true
                ELSE false
            END,
            usable_for_body = CASE
                WHEN qc_status IN ('pass', 'warn') THEN true
                ELSE false
            END,
            reason_messages = qc_reasons
        """
    )


def downgrade() -> None:
    op.drop_column("photoset_entries", "reason_messages")
    op.drop_column("photoset_entries", "reason_codes")
    op.drop_column("photoset_entries", "usable_for_body")
    op.drop_column("photoset_entries", "usable_for_lora")
    op.drop_column("photoset_entries", "bucket")

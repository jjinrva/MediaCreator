"""photoset derivative contract

Revision ID: 0010_derivative_contract
Revises: 0009_ingest_truth_buckets
Create Date: 2026-04-02 23:05:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0010_derivative_contract"
down_revision: str | None = "0009_ingest_truth_buckets"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "photoset_entries",
        sa.Column("body_derivative_storage_object_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "photoset_entries",
        sa.Column("lora_derivative_storage_object_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_photoset_entries_body_derivative_storage",
        "photoset_entries",
        "storage_objects",
        ["body_derivative_storage_object_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_photoset_entries_lora_derivative_storage",
        "photoset_entries",
        "storage_objects",
        ["lora_derivative_storage_object_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_photoset_entries_lora_derivative_storage",
        "photoset_entries",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_photoset_entries_body_derivative_storage",
        "photoset_entries",
        type_="foreignkey",
    )
    op.drop_column("photoset_entries", "lora_derivative_storage_object_id")
    op.drop_column("photoset_entries", "body_derivative_storage_object_id")

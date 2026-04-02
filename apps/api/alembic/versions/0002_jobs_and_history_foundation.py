"""jobs and history foundation

Revision ID: 0002_jobs_and_history_foundation
Revises: 0001_initial_foundation
Create Date: 2026-04-02 00:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0002_jobs_and_history_foundation"
down_revision = "0001_initial_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column("jobs", sa.Column("step_name", sa.String(length=100), nullable=True))
    op.add_column("jobs", sa.Column("error_summary", sa.String(length=255), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("output_asset_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("output_storage_object_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_jobs_output_asset_id_assets",
        "jobs",
        "assets",
        ["output_asset_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_jobs_output_storage_object_id_storage_objects",
        "jobs",
        "storage_objects",
        ["output_storage_object_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(sa.text("UPDATE jobs SET step_name = status WHERE step_name IS NULL"))

    op.add_column(
        "history_events",
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_history_events_job_id_jobs",
        "history_events",
        "jobs",
        ["job_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_history_events_job_id_jobs", "history_events", type_="foreignkey")
    op.drop_column("history_events", "job_id")

    op.drop_constraint(
        "fk_jobs_output_storage_object_id_storage_objects",
        "jobs",
        type_="foreignkey",
    )
    op.drop_constraint("fk_jobs_output_asset_id_assets", "jobs", type_="foreignkey")
    op.drop_column("jobs", "output_storage_object_id")
    op.drop_column("jobs", "output_asset_id")
    op.drop_column("jobs", "error_summary")
    op.drop_column("jobs", "step_name")
    op.drop_column("jobs", "progress_percent")

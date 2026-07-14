"""add sync_metadata table

Revision ID: 0002
"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sync_metadata",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("last_sync_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_status", sa.String, nullable=False, server_default="idle"),
    )


def downgrade() -> None:
    op.drop_table("sync_metadata")

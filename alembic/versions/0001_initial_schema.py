"""initial schema

Revision ID: 0001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "places",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("city", sa.String, nullable=False),
        sa.Column("address", sa.String, nullable=False),
        sa.Column("seats_pattern", sa.String, nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("place_id", UUID(as_uuid=True), sa.ForeignKey("places.id"), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("registration_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("number_of_visitors", sa.Integer, nullable=False, server_default="0"),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_index("ix_events_changed_at", "events", ["changed_at"])
    op.create_index("ix_events_status", "events", ["status"])
    op.create_index("ix_events_event_time", "events", ["event_time"])
    op.create_index("ix_places_city", "places", ["city"])

    op.create_table(
        "registrations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("event_id", UUID(as_uuid=True), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("first_name", sa.String, nullable=False),
        sa.Column("last_name", sa.String, nullable=False),
        sa.Column("seat", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("ticket_id", UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_index("ix_registrations_ticket_id", "registrations", ["ticket_id"], unique=True)


def downgrade() -> None:
    op.drop_table("registrations")
    op.drop_index("ix_events_changed_at", table_name="events")
    op.drop_index("ix_events_status", table_name="events")
    op.drop_index("ix_events_event_time", table_name="events")
    op.drop_index("ix_places_city", table_name="places")
    op.drop_index("ix_registrations_ticket_id", table_name="registrations")
    op.drop_table("events")
    op.drop_table("places")

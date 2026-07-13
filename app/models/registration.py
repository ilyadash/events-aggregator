import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    seat = Column(String, nullable=False)
    email = Column(String, nullable=False)
    ticket_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    registered_at = Column(DateTime(timezone=True), nullable=False)

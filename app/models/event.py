import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False)
    registration_deadline = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False)
    number_of_visitors = Column(Integer, nullable=False, default=0)
    changed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    status_changed_at = Column(DateTime(timezone=True), nullable=False)

    place = relationship("Place", back_populates="events")

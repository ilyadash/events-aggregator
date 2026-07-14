
from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class SyncMetadata(Base):
    __tablename__ = "sync_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_sync_time = Column(DateTime(timezone=True), nullable=True)
    last_changed_at = Column(DateTime(timezone=True), nullable=True)
    sync_status = Column(String, nullable=False, default="idle")

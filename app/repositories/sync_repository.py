from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_metadata import SyncMetadata


class SyncRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_last_changed_at(self) -> datetime | None:
        result = await self.session.execute(
            select(SyncMetadata.last_changed_at).order_by(SyncMetadata.id.desc()).limit(1)
        )
        return result.scalar()

    async def update_sync_status(
        self, status: str, changed_at: datetime | None = None
    ) -> None:
        meta = SyncMetadata(
            last_sync_time=datetime.now().astimezone(),
            last_changed_at=changed_at,
            sync_status=status,
        )
        self.session.add(meta)

import logging
from datetime import datetime

from app.database import async_session_factory
from app.repositories.event_repository import EventRepository
from app.repositories.sync_repository import SyncRepository
from app.services.events_paginator import EventsPaginator
from app.services.provider_client import EventsProviderClient

logger = logging.getLogger(__name__)


async def sync_all() -> None:
    async with async_session_factory() as session:
        sync_repo = SyncRepository(session)
        last_changed = await sync_repo.get_last_changed_at()

    if last_changed is None:
        changed_at = "2000-01-01"
    else:
        changed_at = last_changed.strftime("%Y-%m-%d")

    client = EventsProviderClient()
    logger.info("Sync started, changed_at=%s", changed_at)

    max_changed = None

    try:
        async for event_data in EventsPaginator(client, changed_at):
            async with async_session_factory() as session:
                repo = EventRepository(session)
                await repo.upsert(event_data)
                await session.commit()

            changed = event_data.get("changed_at")
            if changed:
                dt = changed if isinstance(changed, datetime) else datetime.fromisoformat(changed)
                if max_changed is None or dt > max_changed:
                    max_changed = dt

        async with async_session_factory() as session:
            repo = SyncRepository(session)
            await repo.update_sync_status("success", max_changed)
            await session.commit()

        logger.info("Sync completed successfully")
    except Exception as e:
        logger.error("Sync failed: %s", e)
        async with async_session_factory() as session:
            repo = SyncRepository(session)
            await repo.update_sync_status("failed")
            await session.commit()
        raise

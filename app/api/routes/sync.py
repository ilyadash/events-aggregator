import asyncio
import logging

from fastapi import APIRouter

from app.scheduler import run_sync_job

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sync"])


async def _sync_background():
    try:
        await run_sync_job()
        logger.info("Background sync finished")
    except Exception:
        logger.exception("Background sync failed")


@router.post("/api/sync/trigger")
async def trigger_sync():
    asyncio.create_task(_sync_background())
    return {"status": "started"}

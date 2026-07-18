import asyncio

from fastapi import APIRouter

from app.scheduler import run_sync_job

router = APIRouter(tags=["sync"])


@router.post("/api/sync/trigger")
async def trigger_sync():
    asyncio.create_task(run_sync_job())
    return {"status": "started"}

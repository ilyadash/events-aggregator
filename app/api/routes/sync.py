from fastapi import APIRouter

from app.scheduler import run_sync_job

router = APIRouter(tags=["sync"])


@router.post("/api/sync/")
async def trigger_sync():
    await run_sync_job()
    return {"status": "started"}

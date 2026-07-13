from fastapi import APIRouter
from sqlalchemy import select, func

from app.database import async_session_factory
from app.models.event import Event
from app.scheduler import scheduler

router = APIRouter(tags=["health"])


@router.get("/api/health/")
async def health():
    db_ok = False
    try:
        async with async_session_factory() as session:
            await session.execute(select(func.count()).select_from(Event))
            db_ok = True
    except Exception:
        db_ok = False

    return {
        "db": "ok" if db_ok else "error",
        "scheduler_running": scheduler.running,
    }

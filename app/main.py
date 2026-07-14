import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import events, health, sync, tickets
from app.scheduler import run_sync_job, start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_scheduler()
    asyncio.create_task(run_sync_job())
    yield
    stop_scheduler()


app = FastAPI(title="Events Aggregator", lifespan=lifespan)

app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(sync.router)
app.include_router(health.router)

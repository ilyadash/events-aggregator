import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import events, health, sync, tickets
from app.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Events Aggregator", lifespan=lifespan)

app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(sync.router)
app.include_router(health.router)

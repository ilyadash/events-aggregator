import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.routes import events, health, sync, tickets


@pytest.fixture
def api_app() -> FastAPI:
    app = FastAPI()
    app.include_router(events.router)
    app.include_router(tickets.router)
    app.include_router(sync.router)
    app.include_router(health.router)
    return app


@pytest.fixture
async def client(api_app):
    transport = ASGITransport(app=api_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

from app.api.routes import events, health, sync, tickets


@pytest.fixture
def api_app() -> FastAPI:
    app = FastAPI()
    app.include_router(events.router)
    app.include_router(tickets.router)
    app.include_router(sync.router)
    app.include_router(health.router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    return app


@pytest.fixture
async def client(api_app):
    transport = ASGITransport(app=api_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

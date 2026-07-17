import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.routes import events
from app.deps import get_session
from app.repositories.event_repository import EventRepository
from app.usecases.get_event import GetEventUsecase
from app.usecases.list_events import ListEventsUsecase
from tests.integration.conftest import make_event, make_place

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_list_events_usecase(db_session):
    place = make_place()
    db_session.add(place)
    db_session.add(make_event(place=place))
    await db_session.flush()
    db_session.expunge_all()

    repo = EventRepository(db_session)
    uc = ListEventsUsecase(repo)
    response = await uc.do(None, 1, 20, "http://test/api/events")

    assert response.count == 1
    assert len(response.results) == 1
    assert response.results[0].place.city == "Moscow"
    assert response.results[0].status == "published"


@pytest.mark.asyncio
async def test_get_event_usecase(db_session):
    place = make_place()
    db_session.add(place)
    event = make_event(place=place)
    db_session.add(event)
    await db_session.flush()
    db_session.expunge_all()

    repo = EventRepository(db_session)
    uc = GetEventUsecase(repo)
    detail = await uc.do(event.id)

    assert detail is not None
    assert detail.place.seats_pattern == "A-C:1-10"
    assert detail.name == "Concert"


@pytest.mark.asyncio
async def test_api_list_events(db_session):
    place = make_place()
    db_session.add(place)
    db_session.add(make_event(place=place))
    await db_session.flush()
    db_session.expunge_all()

    async def override_get_session():
        yield db_session

    app = FastAPI()
    app.include_router(events.router)
    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/events")

    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["results"][0]["place"]["city"] == "Moscow"


@pytest.mark.asyncio
async def test_api_get_event(db_session):
    place = make_place()
    db_session.add(place)
    event = make_event(place=place)
    db_session.add(event)
    await db_session.flush()
    db_session.expunge_all()

    async def override_get_session():
        yield db_session

    app = FastAPI()
    app.include_router(events.router)
    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/events/{event.id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == str(event.id)
    assert body["place"]["seats_pattern"] == "A-C:1-10"

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.deps import get_get_event_uc, get_get_seats_uc, get_list_events_uc
from app.schemas.event import (
    EventBriefOut,
    EventDetailOut,
    EventListResponse,
    PlaceBriefOut,
    PlaceDetailOut,
)
from app.services.provider_client import ProviderError
from app.usecases.get_event import GetEventUsecase
from app.usecases.get_seats import GetSeatsUsecase
from app.usecases.list_events import ListEventsUsecase


def make_event_brief(event_id=None):
    return EventBriefOut(
        id=event_id or uuid4(),
        name="Concert",
        place=PlaceBriefOut(
            id=uuid4(),
            name="Main Hall",
            city="Moscow",
            address="Tverskaya 1",
        ),
        event_time=datetime(2026, 8, 1, 19, 0, tzinfo=timezone.utc),
        registration_deadline=datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc),
        status="published",
        number_of_visitors=42,
    )


def make_event_detail(event_id):
    return EventDetailOut(
        id=event_id,
        name="Concert",
        place=PlaceDetailOut(
            id=uuid4(),
            name="Main Hall",
            city="Moscow",
            address="Tverskaya 1",
            seats_pattern="A-C:1-10",
        ),
        event_time=datetime(2026, 8, 1, 19, 0, tzinfo=timezone.utc),
        registration_deadline=datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc),
        status="published",
        number_of_visitors=42,
    )


@pytest.fixture
def list_events_uc(api_app):
    uc = AsyncMock(spec=ListEventsUsecase)
    api_app.dependency_overrides[get_list_events_uc] = lambda: uc
    return uc


@pytest.fixture
def get_event_uc(api_app):
    uc = AsyncMock(spec=GetEventUsecase)
    api_app.dependency_overrides[get_get_event_uc] = lambda: uc
    return uc


@pytest.fixture
def get_seats_uc(api_app):
    uc = AsyncMock(spec=GetSeatsUsecase)
    api_app.dependency_overrides[get_get_seats_uc] = lambda: uc
    return uc


@pytest.mark.asyncio
async def test_list_events_ok(client, list_events_uc):
    event = make_event_brief()
    list_events_uc.do.return_value = EventListResponse(
        count=1, next=None, previous=None, results=[event]
    )

    resp = await client.get("/api/events")

    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["next"] is None
    assert body["previous"] is None
    assert len(body["results"]) == 1
    assert body["results"][0]["id"] == str(event.id)
    assert body["results"][0]["name"] == "Concert"
    assert body["results"][0]["place"]["city"] == "Moscow"
    list_events_uc.do.assert_awaited_once_with(
        None, 1, 20, "http://test/api/events"
    )


@pytest.mark.asyncio
async def test_list_events_passes_query_params(client, list_events_uc):
    list_events_uc.do.return_value = EventListResponse(
        count=0, next=None, previous=None, results=[]
    )

    resp = await client.get(
        "/api/events?date_from=2026-01-01&page=2&page_size=5"
    )

    assert resp.status_code == 200
    list_events_uc.do.assert_awaited_once_with(
        "2026-01-01",
        2,
        5,
        "http://test/api/events?date_from=2026-01-01&page=2&page_size=5",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    ["page=0", "page=-1", "page_size=0", "page_size=101"],
)
async def test_list_events_invalid_pagination(client, list_events_uc, query):
    resp = await client.get(f"/api/events?{query}")

    assert resp.status_code == 400
    list_events_uc.do.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_event_ok(client, get_event_uc):
    event_id = uuid4()
    get_event_uc.do.return_value = make_event_detail(event_id)

    resp = await client.get(f"/api/events/{event_id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == str(event_id)
    assert body["place"]["seats_pattern"] == "A-C:1-10"
    assert body["status"] == "published"
    get_event_uc.do.assert_awaited_once_with(event_id)


@pytest.mark.asyncio
async def test_get_event_not_found(client, get_event_uc):
    get_event_uc.do.return_value = None

    resp = await client.get(f"/api/events/{uuid4()}")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Event not found"


@pytest.mark.asyncio
async def test_get_event_invalid_uuid(client, get_event_uc):
    resp = await client.get("/api/events/not-a-uuid")

    assert resp.status_code == 400
    get_event_uc.do.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_seats_ok(client, get_seats_uc):
    event_id = uuid4()
    get_seats_uc.do.return_value = {
        "event_id": event_id,
        "available_seats": ["A1", "A2", "B5"],
    }

    resp = await client.get(f"/api/events/{event_id}/seats")

    assert resp.status_code == 200
    body = resp.json()
    assert body["event_id"] == str(event_id)
    assert body["available_seats"] == ["A1", "A2", "B5"]
    get_seats_uc.do.assert_awaited_once_with(event_id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "detail"),
    [
        (404, "Event not found"),
        (400, "Event is not published"),
        (500, "Provider unavailable"),
    ],
)
async def test_get_seats_provider_error(
    client, get_seats_uc, status_code, detail
):
    get_seats_uc.do.side_effect = ProviderError(status_code, detail)

    resp = await client.get(f"/api/events/{uuid4()}/seats")

    assert resp.status_code == status_code
    assert resp.json()["detail"] == detail

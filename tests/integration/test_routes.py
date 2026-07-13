import uuid
from datetime import datetime, timezone

from app.models.event import Event
from app.models.place import Place
from app.services.event_service import list_events


async def test_client_list_events(client, db_session):
    place = Place(
        id=uuid.uuid4(),
        name="Place",
        city="Moscow",
        address="St",
        seats_pattern="A1-10",
        changed_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    event = Event(
        id=uuid.uuid4(),
        name="API Event",
        place_id=place.id,
        event_time=datetime(2026, 6, 1, tzinfo=timezone.utc),
        registration_deadline=datetime(2026, 5, 30, tzinfo=timezone.utc),
        status="published",
        number_of_visitors=0,
        changed_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        status_changed_at=datetime.now(timezone.utc),
    )
    db_session.add(place)
    db_session.add(event)
    await db_session.commit()

    resp = await client.get("/api/events/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "API Event"
    assert data["items"][0]["place"]["city"] == "Moscow"


async def test_get_event_not_found(client):
    resp = await client.get(f"/api/events/{uuid.uuid4()}/")
    assert resp.status_code == 404


async def test_health(client):
    resp = await client.get("/api/health/")
    assert resp.status_code == 200
    assert "db" in resp.json()

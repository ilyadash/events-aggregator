import uuid
from datetime import datetime, timezone

import pytest

from app.models.event import Event
from app.models.place import Place
from app.services.event_service import list_events, get_event


@pytest.fixture
async def sample_data(db_session):
    place = Place(
        id=uuid.uuid4(),
        name="Test Place",
        city="Moscow",
        address="Test St",
        seats_pattern="A1-10",
        changed_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    event = Event(
        id=uuid.uuid4(),
        name="Test Event",
        place_id=place.id,
        event_time=datetime(2026, 6, 1, tzinfo=timezone.utc),
        registration_deadline=datetime(2026, 5, 30, tzinfo=timezone.utc),
        status="published",
        number_of_visitors=5,
        changed_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        status_changed_at=datetime.now(timezone.utc),
    )
    db_session.add(place)
    db_session.add(event)
    await db_session.commit()
    return place, event


@pytest.mark.asyncio
async def test_list_events(sample_data, db_session):
    place, event = sample_data
    result = await list_events(db_session)
    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].name == "Test Event"
    assert result.items[0].place.city == "Moscow"
    assert result.pages == 1


@pytest.mark.asyncio
async def test_get_event(sample_data, db_session):
    place, event = sample_data
    result = await get_event(db_session, str(event.id))
    assert result is not None
    assert result.name == "Test Event"
    assert result.place.name == "Test Place"


@pytest.mark.asyncio
async def test_filter_by_city(sample_data, db_session):
    place, event = sample_data
    result = await list_events(db_session, city="Moscow")
    assert result.total == 1

    result = await list_events(db_session, city="Spb")
    assert result.total == 0


@pytest.mark.asyncio
async def test_filter_by_status(sample_data, db_session):
    place, event = sample_data
    result = await list_events(db_session, status="published")
    assert result.total == 1

    result = await list_events(db_session, status="new")
    assert result.total == 0


@pytest.mark.asyncio
async def test_filter_by_date(sample_data, db_session):
    place, event = sample_data
    result = await list_events(
        db_session,
        from_date=datetime(2026, 5, 1).date(),
        to_date=datetime(2026, 7, 1).date(),
    )
    assert result.total == 1

    result = await list_events(
        db_session,
        from_date=datetime(2027, 1, 1).date(),
    )
    assert result.total == 0


@pytest.mark.asyncio
async def test_pagination(db_session):
    place = Place(
        id=uuid.uuid4(),
        name="Place",
        city="Moscow",
        address="St",
        seats_pattern="A1-10",
        changed_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(place)
    await db_session.flush()

    for i in range(5):
        e = Event(
            id=uuid.uuid4(),
            name=f"Event {i}",
            place_id=place.id,
            event_time=datetime(2026, 6, i + 1, tzinfo=timezone.utc),
            registration_deadline=datetime(2026, 5, 30, tzinfo=timezone.utc),
            status="published",
            number_of_visitors=0,
            changed_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            status_changed_at=datetime.now(timezone.utc),
        )
        db_session.add(e)
    await db_session.commit()

    result = await list_events(db_session, page=1, size=2)
    assert result.total == 5
    assert len(result.items) == 2
    assert result.pages == 3
    assert result.page == 1

    result = await list_events(db_session, page=3, size=2)
    assert len(result.items) == 1
    assert result.page == 3

import uuid
from datetime import datetime, timezone

import pytest

from app.repositories.event_repository import EventRepository
from tests.integration.conftest import make_event, make_place

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_list_paginated_loads_place(db_session):
    place = make_place()
    db_session.add(place)
    event = make_event(place=place)
    db_session.add(event)
    await db_session.flush()
    db_session.expunge_all()

    repo = EventRepository(db_session)
    rows, total = await repo.list_paginated(None, 1, 20)

    assert len(rows) == 1
    assert total == 1
    assert rows[0].place.id == place.id
    assert rows[0].place.name == place.name
    assert rows[0].place.city == place.city


@pytest.mark.asyncio
async def test_get_by_id_loads_place(db_session):
    place = make_place()
    db_session.add(place)
    event = make_event(place=place)
    db_session.add(event)
    await db_session.flush()
    db_session.expunge_all()

    repo = EventRepository(db_session)
    loaded = await repo.get_by_id(str(event.id))

    assert loaded is not None
    assert loaded.place.id == place.id
    assert loaded.place.seats_pattern == place.seats_pattern


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    repo = EventRepository(db_session)
    result = await repo.get_by_id(str(uuid.uuid4()))
    assert result is None


@pytest.mark.asyncio
async def test_list_paginated_pagination(db_session):
    place = make_place()
    db_session.add(place)
    for i in range(5):
        db_session.add(make_event(place=place, name=f"Event {i}"))
    await db_session.flush()
    db_session.expunge_all()

    repo = EventRepository(db_session)

    rows, total = await repo.list_paginated(None, 1, 2)
    assert len(rows) == 2
    assert total == 5

    rows, total = await repo.list_paginated(None, 3, 2)
    assert len(rows) == 1
    assert total == 5


@pytest.mark.asyncio
async def test_list_paginated_empty(db_session):
    repo = EventRepository(db_session)
    rows, total = await repo.list_paginated(None, 1, 20)
    assert rows == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_paginated_date_filter(db_session):
    place = make_place()
    db_session.add(place)
    dt1 = datetime(2026, 6, 1, 19, 0, tzinfo=timezone.utc)
    dt2 = datetime(2026, 8, 1, 19, 0, tzinfo=timezone.utc)
    db_session.add(make_event(place=place, event_time=dt1))
    db_session.add(make_event(place=place, event_time=dt2))
    await db_session.flush()
    db_session.expunge_all()

    repo = EventRepository(db_session)
    rows, total = await repo.list_paginated("2026-07-01", 1, 20)

    assert total == 1
    assert rows[0].place.id == place.id

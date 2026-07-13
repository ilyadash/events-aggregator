from datetime import datetime

from sqlalchemy import select, func, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.event import Event
from app.models.place import Place
from app.services.provider_client import provider_client


async def upsert_place(session: AsyncSession, data: dict) -> Place:
    existing = await session.get(Place, data["id"])
    if existing is None:
        place = Place(**data)
        session.add(place)
        return place
    for key, val in data.items():
        setattr(existing, key, val)
    return existing


async def upsert_event(session: AsyncSession, data: dict) -> Event:
    place_data = data.pop("place")
    data["place_id"] = place_data["id"]
    await upsert_place(session, place_data)

    existing = await session.get(Event, data["id"])
    if existing is None:
        event = Event(**data)
        session.add(event)
        return event
    for key, val in data.items():
        setattr(existing, key, val)
    return existing


async def sync_all() -> None:
    async with async_session_factory() as session:
        max_changed = await session.execute(
            select(func.max(Event.changed_at))
        )
        max_changed_val: datetime | None = max_changed.scalar()

    if max_changed_val is None:
        changed_at = "2000-01-01"
    else:
        changed_at = max_changed_val.strftime("%Y-%m-%d")

    cursor: str | None = None
    while True:
        resp = await provider_client.fetch_events(changed_at, cursor)
        results = resp.get("results", [])
        async with async_session_factory() as session:
            for item in results:
                await upsert_event(session, item)
            await session.commit()

        cursor = resp.get("next")
        if cursor is None:
            break

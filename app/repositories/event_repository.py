from datetime import datetime

from sqlalchemy import DateTime, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.place import Place


def _convert_datetime_strings(model_class, data: dict) -> dict:
    for col in model_class.__table__.columns:
        if isinstance(col.type, DateTime) and col.name in data:
            val = data[col.name]
            if isinstance(val, str):
                data[col.name] = datetime.fromisoformat(val)
    return data


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: str) -> Event | None:
        result = await self.session.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        date_from: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Event], int]:
        base_q = select(Event).join(Place)

        if date_from:
            base_q = base_q.where(Event.event_time >= date_from)

        count_q = select(func.count()).select_from(base_q.subquery())
        total = (await self.session.execute(count_q)).scalar_one()

        offset = (page - 1) * page_size
        rows_q = base_q.order_by(Event.event_time).offset(offset).limit(page_size)
        rows = (await self.session.execute(rows_q)).scalars().all()

        return list(rows), total

    async def get_max_changed_at(self) -> datetime | None:
        result = await self.session.execute(
            select(func.max(Event.changed_at))
        )
        return result.scalar()

    async def upsert(self, data: dict) -> Event:
        place_data = data.pop("place")
        data["place_id"] = place_data["id"]
        await self._upsert_place(place_data)

        data = _convert_datetime_strings(Event, data)
        existing = await self.session.get(Event, data["id"])
        if existing is None:
            event = Event(**data)
            self.session.add(event)
            return event
        for key, val in data.items():
            setattr(existing, key, val)
        return existing

    async def _upsert_place(self, data: dict) -> Place:
        data = _convert_datetime_strings(Place, data)
        existing = await self.session.get(Place, data["id"])
        if existing is None:
            place = Place(**data)
            self.session.add(place)
            return place
        for key, val in data.items():
            setattr(existing, key, val)
        return existing

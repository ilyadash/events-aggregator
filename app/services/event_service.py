from datetime import date, datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.place import Place
from app.schemas.event import EventListOut, EventOut, PlaceOut


async def list_events(
    session: AsyncSession,
    city: str | None = None,
    status: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = 1,
    size: int = 20,
) -> EventListOut:
    base_q = select(Event).join(Place)

    if city:
        base_q = base_q.where(Place.city == city)
    if status:
        base_q = base_q.where(Event.status == status)
    if from_date:
        base_q = base_q.where(Event.event_time >= from_date)
    if to_date:
        base_q = base_q.where(Event.event_time <= to_date)

    count_q = select(func.count()).select_from(base_q.subquery())
    total = (await session.execute(count_q)).scalar_one()

    offset = (page - 1) * size
    rows_q = base_q.order_by(Event.event_time).offset(offset).limit(size)
    rows = (await session.execute(rows_q)).scalars().all()

    items = [
        EventOut(
            id=e.id,
            name=e.name,
            place=PlaceOut.model_validate(e.place),
            event_time=e.event_time,
            registration_deadline=e.registration_deadline,
            status=e.status,
            number_of_visitors=e.number_of_visitors,
            changed_at=e.changed_at,
            created_at=e.created_at,
            status_changed_at=e.status_changed_at,
        )
        for e in rows
    ]

    pages = max(1, (total + size - 1) // size)

    return EventListOut(items=items, total=total, page=page, size=size, pages=pages)


async def get_event(session: AsyncSession, event_id: str) -> EventOut | None:
    result = await session.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    if event is None:
        return None
    return EventOut(
        id=event.id,
        name=event.name,
        place=PlaceOut.model_validate(event.place),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
        changed_at=event.changed_at,
        created_at=event.created_at,
        status_changed_at=event.status_changed_at,
    )

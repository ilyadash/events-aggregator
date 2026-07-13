import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.registration import Registration
from app.schemas.registration import RegisterOut, UnregisterOut
from app.services.provider_client import provider_client, ProviderError
from app.utils.seats_pattern import parse_seats_pattern


async def register(
    session: AsyncSession, event_id: uuid.UUID, body: dict
) -> RegisterOut:
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if event is None:
        raise ProviderError(404, "Event not found")
    if event.status != "published":
        raise ProviderError(400, "Event is not published")
    if datetime.now(timezone.utc) > event.registration_deadline:
        raise ProviderError(400, "Registration deadline has passed")

    seats = await provider_client.fetch_seats(event_id)
    if body["seat"] not in seats:
        raise ProviderError(400, "Seat is not available")

    resp = await provider_client.register(event_id, body)
    ticket_id = uuid.UUID(resp["ticket_id"]) if isinstance(resp["ticket_id"], str) else resp["ticket_id"]

    reg = Registration(
        event_id=event_id,
        first_name=body["first_name"],
        last_name=body["last_name"],
        seat=body["seat"],
        email=body["email"],
        ticket_id=ticket_id,
        registered_at=datetime.now(timezone.utc),
    )
    session.add(reg)
    await session.commit()

    return RegisterOut(ticket_id=ticket_id)


async def unregister(
    session: AsyncSession, event_id: uuid.UUID, ticket_id: uuid.UUID
) -> UnregisterOut:
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if event is None:
        raise ProviderError(404, "Event not found")

    result = await session.execute(
        select(Registration).where(Registration.ticket_id == ticket_id)
    )
    reg = result.scalar_one_or_none()
    if reg is None:
        raise ProviderError(404, "Registration not found")

    if datetime.now(timezone.utc) > event.event_time:
        raise ProviderError(400, "Event has already passed")

    await provider_client.unregister(event_id, str(ticket_id))

    await session.delete(reg)
    await session.commit()
    return UnregisterOut(success=True)

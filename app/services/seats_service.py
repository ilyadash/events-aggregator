from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.schemas.seats import SeatsOut
from app.services.provider_client import provider_client, ProviderError


async def get_seats(session: AsyncSession, event_id: UUID) -> SeatsOut:
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if event is None:
        raise ProviderError(404, "Event not found")
    if event.status != "published":
        raise ProviderError(400, "Event is not published")

    seats = await provider_client.fetch_seats(event_id)
    return SeatsOut(seats=seats)

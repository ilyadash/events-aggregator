import time
from uuid import UUID

from app.config import settings
from app.repositories.event_repository import EventRepository
from app.services.provider_client import EventsProviderClient, ProviderError

_seats_cache: dict[UUID, tuple[float, list[str]]] = {}


class GetSeatsUsecase:
    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepository,
    ):
        self.client = client
        self.events = events

    async def do(self, event_id: UUID) -> dict:
        event = await self.events.get_by_id(str(event_id))
        if not event:
            raise ProviderError(404, "Event not found")
        if event.status != "published":
            raise ProviderError(400, "Event is not published")

        now = time.time()
        cached = _seats_cache.get(event_id)
        if cached and now - cached[0] < settings.SEATS_CACHE_TTL:
            return {"event_id": event_id, "available_seats": cached[1]}

        seats = await self.client.fetch_seats(event_id)
        _seats_cache[event_id] = (now, seats)
        return {"event_id": event_id, "available_seats": seats}

from datetime import datetime, timezone
from uuid import UUID

from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.provider_client import EventsProviderClient, ProviderError


class CancelTicketUsecase:
    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepository,
        tickets: TicketRepository,
    ):
        self.client = client
        self.events = events
        self.tickets = tickets

    async def do(self, ticket_id: UUID) -> bool:
        reg = await self.tickets.get_by_ticket_id(ticket_id)
        if not reg:
            raise ProviderError(404, "Registration not found")

        event = await self.events.get_by_id(str(reg.event_id))
        if not event:
            raise ProviderError(404, "Event not found")
        if datetime.now(timezone.utc) > event.event_time:
            raise ProviderError(400, "Event has already passed")

        await self.client.unregister(reg.event_id, str(ticket_id))
        await self.tickets.delete(ticket_id)
        return True

from datetime import datetime, timezone
from uuid import UUID

from app.models.event_status import EventStatus
from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.provider_client import EventsProviderClient, ProviderError


class CreateTicketUsecase:
    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepository,
        tickets: TicketRepository,
    ):
        self.client = client
        self.events = events
        self.tickets = tickets

    async def do(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> UUID:
        event = await self.events.get_by_id(event_id)
        if not event:
            raise ProviderError(404, "Event not found")
        if event.status != EventStatus.PUBLISHED:
            raise ProviderError(400, "Event is not published")
        if datetime.now(timezone.utc) > event.registration_deadline:
            raise ProviderError(400, "Registration deadline has passed")

        seats = await self.client.fetch_seats(UUID(event_id))
        if seat not in seats:
            raise ProviderError(400, "Seat is not available")

        resp = await self.client.register(
            UUID(event_id),
            {"first_name": first_name, "last_name": last_name, "seat": seat, "email": email},
        )
        ticket_id = UUID(resp["ticket_id"])

        await self.tickets.create(
            event_id=event_id,
            ticket_id=str(ticket_id),
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
            registered_at=datetime.now(timezone.utc),
        )

        return ticket_id

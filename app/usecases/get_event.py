from uuid import UUID

from app.repositories.event_repository import EventRepository
from app.schemas.event import EventDetailOut, PlaceDetailOut


class GetEventUsecase:
    def __init__(self, events: EventRepository):
        self.events = events

    async def do(self, event_id: UUID) -> EventDetailOut | None:
        event = await self.events.get_by_id(str(event_id))
        if event is None:
            return None
        return EventDetailOut(
            id=event.id,
            name=event.name,
            place=PlaceDetailOut(
                id=event.place.id,
                name=event.place.name,
                city=event.place.city,
                address=event.place.address,
                seats_pattern=event.place.seats_pattern,
            ),
            event_time=event.event_time,
            registration_deadline=event.registration_deadline,
            status=event.status,
            number_of_visitors=event.number_of_visitors,
        )

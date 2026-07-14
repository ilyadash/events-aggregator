from app.repositories.event_repository import EventRepository
from app.schemas.event import EventBriefOut, EventListResponse, PlaceBriefOut


class ListEventsUsecase:
    def __init__(self, events: EventRepository):
        self.events = events

    async def do(
        self, date_from: str | None, page: int, page_size: int, base_url: str
    ) -> EventListResponse:
        rows, total = await self.events.list_paginated(date_from, page, page_size)

        results = [
            EventBriefOut(
                id=e.id,
                name=e.name,
                place=PlaceBriefOut(
                    id=e.place.id,
                    name=e.place.name,
                    city=e.place.city,
                    address=e.place.address,
                ),
                event_time=e.event_time,
                registration_deadline=e.registration_deadline,
                status=e.status,
                number_of_visitors=e.number_of_visitors,
            )
            for e in rows
        ]

        next_url = None
        previous_url = None
        last_page = max(1, (total + page_size - 1) // page_size)

        if page < last_page:
            next_url = f"{base_url}?page={page + 1}"
            if date_from:
                next_url += f"&date_from={date_from}"
        if page > 1:
            previous_url = f"{base_url}?page={page - 1}"
            if date_from:
                previous_url += f"&date_from={date_from}"

        return EventListResponse(
            count=total,
            next=next_url,
            previous=previous_url,
            results=results,
        )

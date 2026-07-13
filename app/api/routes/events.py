from datetime import date

from fastapi import APIRouter, HTTPException

from app.api.deps import PaginationDep, SessionDep
from app.schemas.event import EventListOut, EventOut
from app.services import event_service
from app.services.provider_client import ProviderError

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/")
async def list_events(
    session: SessionDep,
    pagination: PaginationDep,
    city: str | None = None,
    status: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> EventListOut:
    page, size = pagination
    return await event_service.list_events(
        session, city=city, status=status,
        from_date=from_date, to_date=to_date,
        page=page, size=size,
    )


@router.get("/{event_id}")
async def get_event(session: SessionDep, event_id: str) -> EventOut:
    event = await event_service.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

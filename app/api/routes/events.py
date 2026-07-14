from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from app.deps import (
    GetEventUCDep,
    GetSeatsUCDep,
    ListEventsUCDep,
    PaginationDep,
)
from app.schemas.event import EventDetailOut, EventListResponse
from app.schemas.seats import SeatsOut
from app.services.provider_client import ProviderError

router = APIRouter(tags=["events"])


@router.get("/api/events")
async def list_events(
    request: Request,
    uc: ListEventsUCDep,
    pagination: PaginationDep,
    date_from: str | None = None,
) -> EventListResponse:
    page, page_size = pagination
    return await uc.do(date_from, page, page_size, str(request.url))


@router.get("/api/events/{event_id}")
async def get_event(uc: GetEventUCDep, event_id: UUID) -> EventDetailOut:
    event = await uc.do(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/api/events/{event_id}/seats")
async def get_seats(uc: GetSeatsUCDep, event_id: UUID) -> SeatsOut:
    try:
        result = await uc.do(event_id)
        return SeatsOut(**result)
    except ProviderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

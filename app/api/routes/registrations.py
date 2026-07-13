from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.schemas.registration import RegisterIn, RegisterOut, UnregisterIn, UnregisterOut
from app.schemas.seats import SeatsOut
from app.services import seats_service, registration_service
from app.services.provider_client import ProviderError

router = APIRouter(prefix="/api/events/{event_id}", tags=["registrations"])


@router.get("/seats/")
async def get_seats(session: SessionDep, event_id: UUID) -> SeatsOut:
    try:
        return await seats_service.get_seats(session, event_id)
    except ProviderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/register/", status_code=201)
async def register(
    session: SessionDep, event_id: UUID, body: RegisterIn
) -> RegisterOut:
    try:
        return await registration_service.register(
            session, event_id, body.model_dump()
        )
    except ProviderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/unregister/")
async def unregister(
    session: SessionDep, event_id: UUID, body: UnregisterIn
) -> UnregisterOut:
    try:
        return await registration_service.unregister(
            session, event_id, body.ticket_id
        )
    except ProviderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

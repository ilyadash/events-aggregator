from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.deps import CancelTicketUCDep, CreateTicketUCDep
from app.schemas.registration import RegisterIn, RegisterOut, UnregisterOut
from app.services.provider_client import ProviderError

router = APIRouter(tags=["tickets"])


@router.post("/api/tickets", status_code=201)
async def create_ticket(
    uc: CreateTicketUCDep,
    body: RegisterIn,
) -> RegisterOut:
    try:
        ticket_id = await uc.do(
            event_id=str(body.event_id),
            first_name=body.first_name,
            last_name=body.last_name,
            email=str(body.email),
            seat=body.seat,
        )
        return RegisterOut(ticket_id=ticket_id)
    except ProviderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete("/api/tickets/{ticket_id}")
async def cancel_ticket(
    uc: CancelTicketUCDep,
    ticket_id: UUID,
) -> UnregisterOut:
    try:
        success = await uc.do(ticket_id)
        return UnregisterOut(success=success)
    except ProviderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

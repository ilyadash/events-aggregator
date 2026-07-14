from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.repositories.event_repository import EventRepository
from app.repositories.sync_repository import SyncRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.provider_client import EventsProviderClient
from app.usecases.cancel_ticket import CancelTicketUsecase
from app.usecases.create_ticket import CreateTicketUsecase
from app.usecases.get_event import GetEventUsecase
from app.usecases.get_seats import GetSeatsUsecase
from app.usecases.list_events import ListEventsUsecase


async def get_session():
    async with async_session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_provider_client() -> EventsProviderClient:
    return EventsProviderClient()


ProviderClientDep = Annotated[EventsProviderClient, Depends(get_provider_client)]


def get_event_repo(session: SessionDep) -> EventRepository:
    return EventRepository(session)


EventRepoDep = Annotated[EventRepository, Depends(get_event_repo)]


def get_ticket_repo(session: SessionDep) -> TicketRepository:
    return TicketRepository(session)


TicketRepoDep = Annotated[TicketRepository, Depends(get_ticket_repo)]


def get_sync_repo(session: SessionDep) -> SyncRepository:
    return SyncRepository(session)


SyncRepoDep = Annotated[SyncRepository, Depends(get_sync_repo)]


def get_list_events_uc(events: EventRepoDep) -> ListEventsUsecase:
    return ListEventsUsecase(events)


ListEventsUCDep = Annotated[ListEventsUsecase, Depends(get_list_events_uc)]


def get_get_event_uc(events: EventRepoDep) -> GetEventUsecase:
    return GetEventUsecase(events)


GetEventUCDep = Annotated[GetEventUsecase, Depends(get_get_event_uc)]


def get_get_seats_uc(
    client: ProviderClientDep,
    events: EventRepoDep,
) -> GetSeatsUsecase:
    return GetSeatsUsecase(client, events)


GetSeatsUCDep = Annotated[GetSeatsUsecase, Depends(get_get_seats_uc)]


def get_create_ticket_uc(
    client: ProviderClientDep,
    events: EventRepoDep,
    tickets: TicketRepoDep,
) -> CreateTicketUsecase:
    return CreateTicketUsecase(client, events, tickets)


CreateTicketUCDep = Annotated[CreateTicketUsecase, Depends(get_create_ticket_uc)]


def get_cancel_ticket_uc(
    client: ProviderClientDep,
    events: EventRepoDep,
    tickets: TicketRepoDep,
) -> CancelTicketUsecase:
    return CancelTicketUsecase(client, events, tickets)


CancelTicketUCDep = Annotated[CancelTicketUsecase, Depends(get_cancel_ticket_uc)]


async def pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> tuple[int, int]:
    return page, page_size


PaginationDep = Annotated[tuple[int, int], Depends(pagination_params)]

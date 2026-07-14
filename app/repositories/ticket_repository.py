from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.registration import Registration


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        event_id: str,
        ticket_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
        registered_at,
    ) -> None:
        reg = Registration(
            event_id=UUID(event_id),
            ticket_id=UUID(ticket_id),
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
            registered_at=registered_at,
        )
        self.session.add(reg)

    async def get_by_ticket_id(self, ticket_id: UUID) -> Registration | None:
        result = await self.session.execute(
            select(Registration).where(Registration.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, ticket_id: UUID) -> None:
        result = await self.session.execute(
            select(Registration).where(Registration.ticket_id == ticket_id)
        )
        reg = result.scalar_one_or_none()
        if reg:
            await self.session.delete(reg)

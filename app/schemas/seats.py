from uuid import UUID

from pydantic import BaseModel


class SeatsOut(BaseModel):
    event_id: UUID
    available_seats: list[str]

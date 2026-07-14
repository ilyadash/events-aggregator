from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterIn(BaseModel):
    event_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    seat: str


class RegisterOut(BaseModel):
    ticket_id: UUID


class UnregisterOut(BaseModel):
    success: bool

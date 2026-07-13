from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterIn(BaseModel):
    first_name: str
    last_name: str
    seat: str
    email: EmailStr


class RegisterOut(BaseModel):
    ticket_id: UUID


class UnregisterIn(BaseModel):
    ticket_id: UUID


class UnregisterOut(BaseModel):
    success: bool

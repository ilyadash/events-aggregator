from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PlaceBriefOut(BaseModel):
    id: UUID
    name: str
    city: str
    address: str


class PlaceDetailOut(BaseModel):
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: str


class EventBriefOut(BaseModel):
    id: UUID
    name: str
    place: PlaceBriefOut
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class EventDetailOut(BaseModel):
    id: UUID
    name: str
    place: PlaceDetailOut
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class EventListResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventBriefOut]

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


class PlaceOut(BaseModel):
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: str
    changed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class EventOut(BaseModel):
    id: UUID
    name: str
    place: PlaceOut
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    changed_at: datetime
    created_at: datetime
    status_changed_at: datetime

    model_config = {"from_attributes": True}


class EventListOut(BaseModel):
    items: list[EventOut]
    total: int
    page: int
    size: int
    pages: int

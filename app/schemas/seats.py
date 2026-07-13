from pydantic import BaseModel


class SeatsOut(BaseModel):
    seats: list[str]

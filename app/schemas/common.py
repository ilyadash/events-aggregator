from pydantic import BaseModel, Field


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int

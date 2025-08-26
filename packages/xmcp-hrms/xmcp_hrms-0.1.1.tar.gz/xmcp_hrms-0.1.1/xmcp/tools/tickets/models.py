from typing import List, Optional

from typing import List, Optional

from pydantic import BaseModel, Field


class TicketEntry(BaseModel):
    """Represents a single ticket entry."""

    id: str = Field(alias="Id")
    category: Optional[str] = None
    status: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = {"populate_by_name": True}


class Paginate(BaseModel):
    totalRecords: int
    totalPerpage: int
    totalPage: int
    currentPage: int
    nextPage: Optional[int] = None
    previousPage: Optional[int] = None


class TicketsResponse(BaseModel):
    statusCode: int
    statusMessage: str
    data: List[TicketEntry]
    paginate: Paginate


class TicketOperationResponse(BaseModel):
    """Generic response for ticket creation or submission."""

    statusCode: int
    statusMessage: str
    data: Optional[dict] = None

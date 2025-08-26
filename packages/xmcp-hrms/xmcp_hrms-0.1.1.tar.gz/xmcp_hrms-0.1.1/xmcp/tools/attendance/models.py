from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AttendanceEntry(BaseModel):
    """Represents a single attendance record."""

    id: str = Field(alias="Id")
    attendanceDate: date
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    source: Optional[str] = None
    inStatus: Optional[str] = None
    outStatus: Optional[str] = None
    category: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(populate_by_name=True)


class Paginate(BaseModel):
    totalRecords: int
    totalPerpage: int
    totalPage: int
    currentPage: int
    nextPage: Optional[int] = None
    previousPage: Optional[int] = None


class AttendanceResponse(BaseModel):
    """Response model for the attendance search endpoint."""

    statusCode: int
    statusMessage: str
    data: List[AttendanceEntry]
    paginate: Paginate

from datetime import date, datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field


class Holiday(BaseModel):
    """Represents a holiday returned by the HRMS API."""

    holidayDate: date
    descText: str
    type: str


class HolidaysResponse(BaseModel):
    """Response model for the holidays endpoint."""

    statusCode: int
    statusMessage: str
    data: List[Holiday]
    rhBalance: Optional[int] = None


class LeaveEntry(BaseModel):
    """Represents a single leave or comp-off entry."""

    id: str = Field(alias="Id")
    category: str
    type: str
    status: str
    leaveDate: date
    leaveCount: float
    comments: Optional[str] = None
    salaryYear: Optional[str] = None
    salaryMonth: Optional[str] = None
    subStatus: Optional[str] = None
    appliedDate: date
    approvedDate: Optional[date] = None
    employeeId: str
    employeeFinancialYearId: str
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(populate_by_name=True)


class LeavesResponse(BaseModel):
    """Response model for the leaves endpoint."""

    statusCode: int
    statusMessage: str
    data: List[LeaveEntry]


class ApplyLeaveRequest(BaseModel):
    """Payload for applying a leave (not comp-off)."""
    model_config = ConfigDict(extra="forbid")  # reject unknown keys

    # Defaults to "Debit" and only allows "Debit"
    type: Literal["Debit"] = Field(
        "Debit",
        description="Transaction type (always 'Debit' when applying a leave)",
    )
    category: str = Field(
        "Debit",
        description="Leave category (defaults to 'Debit' if omitted)",
    )
    leaveCount: float = Field(
        ..., description="Number of leave days or comp-off units being requested",
    )
    leaveDate: date = Field(
        ..., description="Date for the requested leave in YYYY-MM-DD format",
    )
    comments: Optional[str] = Field(
        None, description="Optional explanation or reason for the leave",
    )
    status: str = Field(
        "Pending Approval",
        description="Initial application status (defaults to 'Pending Approval')",
    )


class ApplyCompOffRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str = Field(..., description="e.g., 'Credit'")
    category: str = Field(..., description="Must be 'Comp-Off'")
    compOffCount: float = Field(..., description="Units of comp-off to credit")
    workingDate: date = Field(..., description="YYYY-MM-DD day you worked")
    description: str = Field(..., description="What you worked on")
    status: str = Field(..., description="e.g., 'Pending Approval'")


class ApplyLeaveData(BaseModel):
    """Information about the newly created leave entry."""

    id: str = Field(alias="Id")
    leaveDate: date
    leaveCount: float
    comments: Optional[str] = None
    category: str
    type: str
    status: str
    employeeFinancialYearId: str
    employeeId: str
    appliedDate: date
    updatedAt: datetime
    createdAt: datetime

    model_config = ConfigDict(populate_by_name=True)


class ApplyLeaveResponse(BaseModel):
    """Response model for applying leave."""

    statusCode: int
    statusMessage: str
    data: Optional[ApplyLeaveData] = None
    error: Optional[str] = None

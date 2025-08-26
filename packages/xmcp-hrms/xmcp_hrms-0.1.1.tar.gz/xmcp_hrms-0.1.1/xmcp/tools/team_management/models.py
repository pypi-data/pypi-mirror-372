from datetime import date, datetime
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class LedgerEntry(BaseModel):
    id: str = Field(alias="Id")
    category: str
    type: str
    status: str
    employeeFinancialYearId: str
    leaveDate: date
    leaveCount: float
    comments: Optional[str] = None
    approvedDate: Optional[date] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(populate_by_name=True)


class LeaveBalance(BaseModel):
    leavesAccured: float | int
    leavesConsumed: float | int
    leavesRemaining: float | int
    overConsumedLeaves: float | int
    compOffAccrued: float | int
    compOffConsumed: float | int
    compOffLapsed: float | int
    rhBalance: Optional[float | int] = None
    compOffRemaining: float | int
    paternityRemaining: Optional[float | int] = None
    maternityRemaining: Optional[float | int] = None
    maternityConsumed: Optional[float | int] = None


class TeamLedgerResponse(BaseModel):
    statusCode: int
    statusMessage: str
    data: List[LedgerEntry]
    leaveBalance: LeaveBalance

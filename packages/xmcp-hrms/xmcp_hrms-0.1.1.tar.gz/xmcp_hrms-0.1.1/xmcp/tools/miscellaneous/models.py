from datetime import date
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class FinancialYear(BaseModel):
    id: str = Field(alias="Id")
    fyStartDate: date
    fyEndDate: date
    financialYear: str
    employeeId: str

    model_config = {"populate_by_name": True}


class FinancialYearsResponse(BaseModel):
    statusCode: int
    statusMessage: str
    data: List[FinancialYear]


class ProfileResponse(BaseModel):
    statusCode: int
    statusMessage: str
    data: dict

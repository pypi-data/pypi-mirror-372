from fastapi import APIRouter, Header, HTTPException
import httpx

from .client import MiscClient
from .models import FinancialYearsResponse, ProfileResponse

router = APIRouter()
client = MiscClient()


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/financial-years", response_model=FinancialYearsResponse)
async def financial_years(authorization: str = Header(...)) -> FinancialYearsResponse:
    """Retrieve financial year data for current employee."""
    try:
        return await client.get_financial_years(authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/employees/{employee_id}", response_model=ProfileResponse)
async def employee_profile(
    employee_id: str, authorization: str = Header(...)
) -> ProfileResponse:
    """Retrieve HRMS profile for the specified employee."""
    try:
        return await client.get_employee_profile(employee_id, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

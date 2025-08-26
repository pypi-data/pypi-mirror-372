import os
from dotenv import load_dotenv
import httpx

from .models import FinancialYearsResponse, ProfileResponse

load_dotenv()

class MiscClient:
    """Client for miscellaneous APIs such as profile and financial years."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or os.getenv("HRMS_API_BASE_URL")
        if not self.base_url:
            raise RuntimeError("HRMS_API_BASE_URL is not configured")
        self.timeout = timeout

    async def get_financial_years(self, auth_header: str) -> FinancialYearsResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/payroll/employeeFinancialYears/my",
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return FinancialYearsResponse.model_validate(response.json())

    async def get_employee_profile(
        self, employee_id: str, auth_header: str
    ) -> ProfileResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/app/employees/id",
                params={"id": employee_id},
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return ProfileResponse.model_validate(response.json())

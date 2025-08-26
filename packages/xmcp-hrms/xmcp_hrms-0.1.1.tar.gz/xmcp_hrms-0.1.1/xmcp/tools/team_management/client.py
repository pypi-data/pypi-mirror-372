import os
from dotenv import load_dotenv
import httpx

from .models import TeamLedgerResponse

load_dotenv()

class TeamManagementClient:
    """Client for team management related APIs."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or os.getenv("HRMS_API_BASE_URL")
        if not self.base_url:
            raise RuntimeError("HRMS_API_BASE_URL is not configured")
        self.timeout = timeout

    async def get_team_ledger(
        self, emp_id: str, fy: str, auth_header: str
    ) -> TeamLedgerResponse:
        params = {"empId": emp_id, "fy": fy}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/attendance/leaves/my-team-ledger",
                params=params,
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return TeamLedgerResponse.model_validate(response.json())

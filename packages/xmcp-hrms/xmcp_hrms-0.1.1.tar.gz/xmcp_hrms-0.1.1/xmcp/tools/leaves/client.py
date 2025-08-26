import os
from dotenv import load_dotenv
import httpx

from .models import (
    ApplyLeaveRequest,
    ApplyLeaveResponse,
    HolidaysResponse,
    LeavesResponse,
    ApplyCompOffRequest
)

load_dotenv()


class LeavesClient:
    """Client for interacting with leave-related HRMS APIs."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = (base_url or os.getenv("HRMS_API_BASE_URL") or "").rstrip("/")
        if not self.base_url:
            raise RuntimeError("HRMS_API_BASE_URL is not configured")
        self.timeout = timeout

    async def get_holidays(self, year: int, auth_header: str) -> HolidaysResponse:
        """Retrieve holiday information for the given year."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/app/employees/holidays",
                params={"year": year},
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return HolidaysResponse.model_validate(response.json())

    async def get_leaves(self, fy_id: str, auth_header: str) -> LeavesResponse:
        """Retrieve leave entries for the specified financial year id."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/attendance/leaves/my-leaves",
                params={"fyId": fy_id},
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return LeavesResponse.model_validate(response.json())

    async def apply_leave(
        self, payload: ApplyLeaveRequest, auth_header: str
    ) -> ApplyLeaveResponse:
        """Submit a leave application."""
        # IMPORTANT: use mode="json" so date fields serialize to ISO strings
        json_payload = payload.model_dump(mode="json")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/attendance/leaves/apply",
                json=json_payload,
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return ApplyLeaveResponse.model_validate(response.json())

    async def apply_comp_off(
        self, payload: ApplyCompOffRequest, auth_header: str
    ) -> ApplyLeaveResponse:
        """Submit a comp-off application."""
        json_payload = payload.model_dump(mode="json")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/attendance/leaves/apply/comp-off",
                json=json_payload,
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return ApplyLeaveResponse.model_validate(response.json())

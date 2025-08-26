import os
from dotenv import load_dotenv
import httpx

from .models import TicketsResponse, TicketOperationResponse

load_dotenv()

class TicketsClient:
    """Client for interacting with ticket related APIs."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or os.getenv("HRMS_API_BASE_URL")
        if not self.base_url:
            raise RuntimeError("HRMS_API_BASE_URL is not configured")
        self.timeout = timeout

    async def get_my_tickets(
        self, emp_id: str, status: str, page: int, auth_header: str
    ) -> TicketsResponse:
        """Retrieve tickets for the authenticated employee."""

        params = {"id": emp_id, "status": status, "page": page}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/ticket-asset/tickets/my/tickets",
                params=params,
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return TicketsResponse.model_validate(response.json())

    async def raise_ticket(
        self, auth_header: str, form_data: dict | None = None
    ) -> TicketOperationResponse:
        """Create a new ticket draft."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/ticket-asset/tickets/employee",
                data=form_data or {},
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return TicketOperationResponse.model_validate(response.json())

    async def submit_ticket(
        self, ticket_id: str, auth_header: str
    ) -> TicketOperationResponse:
        """Submit a draft ticket."""
        params = {"id": ticket_id}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/ticket-asset/tickets/submit",
                params=params,
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return TicketOperationResponse.model_validate(response.json())

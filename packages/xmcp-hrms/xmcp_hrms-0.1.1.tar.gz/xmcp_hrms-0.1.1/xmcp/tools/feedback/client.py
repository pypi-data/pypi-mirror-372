import os
from dotenv import load_dotenv
import httpx

from .models import (
    AddFeedbackRequest,
    AddFeedbackResponse,
    RMFeedbacksResponse,
    FeedbackLevelsResponse,
)

load_dotenv()

class FeedbackClient:
    """Client for interacting with feedback related APIs."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or os.getenv("HRMS_API_BASE_URL")
        if not self.base_url:
            raise RuntimeError("HRMS_API_BASE_URL is not configured")
        self.timeout = timeout

    async def add_feedback(
        self, payload: AddFeedbackRequest, auth_header: str
    ) -> AddFeedbackResponse:
        """Submit feedback for a team member."""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/app/employeeNotes/addgenericNote",
                json=payload.model_dump(),
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return AddFeedbackResponse.model_validate(response.json())

    async def get_rm_feedbacks(
        self, auth_header: str, emp_id: str = ""
    ) -> RMFeedbacksResponse:
        """Retrieve RM feedback entries."""
        params = {"id": emp_id, "tab": "RMFeedbacks"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/app/employeeNotes/genericNotes",
                params=params,
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return RMFeedbacksResponse.model_validate(response.json())

    async def get_feedback_levels(
        self, auth_header: str
    ) -> FeedbackLevelsResponse:
        """List users available for feedback."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/app/employeeNotes/feedbackLevels",
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return FeedbackLevelsResponse.model_validate(response.json())

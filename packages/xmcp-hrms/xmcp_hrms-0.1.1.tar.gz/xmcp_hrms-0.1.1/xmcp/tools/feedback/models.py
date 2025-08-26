from datetime import date
from typing import Optional

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class AddFeedbackRequest(BaseModel):
    """Payload for submitting feedback for a team member."""

    nextFollowUpDate: date
    employeeId: str
    description: str
    outcome: str
    stars: int
    type: str
    year: int
    month: int


class AddFeedbackResponse(BaseModel):
    """Response model for add feedback API."""

    statusCode: int
    statusMessage: str
    data: Optional[dict] = None


class RMFeedbacksResponse(BaseModel):
    """Response model for retrieving RM feedback entries."""

    statusCode: int
    statusMessage: str
    data: list[dict]
    paginate: Optional[dict] = None


class FeedbackLevelsResponse(BaseModel):
    """Response model for listing feedback levels/users."""

    statusCode: int
    statusMessage: str
    data: list[dict]

from fastapi import APIRouter, Header, HTTPException, Query
import httpx

from .client import FeedbackClient
from .models import (
    AddFeedbackRequest,
    AddFeedbackResponse,
    RMFeedbacksResponse,
    FeedbackLevelsResponse,
)

router = APIRouter(prefix="/feedback")
client = FeedbackClient()


@router.post("/add", response_model=AddFeedbackResponse)
async def add_feedback(
    body: AddFeedbackRequest, authorization: str = Header(...)
) -> AddFeedbackResponse:
    """Submit feedback for a team member."""
    try:
        return await client.add_feedback(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/rm-feedbacks", response_model=RMFeedbacksResponse)
async def rm_feedbacks(
    authorization: str = Header(...), id: str = Query("")
) -> RMFeedbacksResponse:
    """Retrieve RM feedback entries for the given employee."""
    try:
        return await client.get_rm_feedbacks(authorization, id)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/levels", response_model=FeedbackLevelsResponse)
async def feedback_levels(
    authorization: str = Header(...),
) -> FeedbackLevelsResponse:
    """List users available in feedback levels."""
    try:
        return await client.get_feedback_levels(authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

from fastapi import APIRouter, Header, HTTPException, Query
import httpx

from .client import TicketsClient
from .models import TicketOperationResponse, TicketsResponse

router = APIRouter(prefix="/tickets")
client = TicketsClient()


@router.get("/my", response_model=TicketsResponse)
async def my_tickets(
    id: str = Query(...),
    status: str = Query(...),
    page: int = Query(1, ge=1),
    authorization: str = Header(...),
) -> TicketsResponse:
    """Retrieve tickets for the authenticated employee."""
    try:
        return await client.get_my_tickets(id, status, page, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/draft", response_model=TicketOperationResponse)
async def raise_ticket(
    authorization: str = Header(...),
) -> TicketOperationResponse:
    """Create a new ticket draft."""
    try:
        return await client.raise_ticket(authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/submit", response_model=TicketOperationResponse)
async def submit_ticket(
    id: str = Query(...), authorization: str = Header(...)
) -> TicketOperationResponse:
    """Submit a draft ticket."""
    try:
        return await client.submit_ticket(id, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

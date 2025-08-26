from fastapi import APIRouter, Header, HTTPException, Query
import httpx
from fastapi import APIRouter, Depends
import xmcp.tools.leaves.client as leaves_client_module
import xmcp.auth_context as auth_context
import xmcp.tools.leaves.models as leaves_models

LeavesClient = leaves_client_module.LeavesClient
auth_header_getter = auth_context.auth_header_getter
ApplyLeaveRequest = leaves_models.ApplyLeaveRequest
ApplyLeaveResponse = leaves_models.ApplyLeaveResponse
HolidaysResponse = leaves_models.HolidaysResponse
LeavesResponse = leaves_models.LeavesResponse
ApplyCompOffRequest = leaves_models.ApplyCompOffRequest

# Single client used by the FastAPI routes; tests patch methods on this instance.
client = LeavesClient()

# Endpoints live at the API root: /holidays, /leaves, /leaves/apply
router = APIRouter(tags=["leaves"])

@router.get("/holidays", response_model=HolidaysResponse)
async def holidays(
    year: int = Query(..., ge=1900, le=2100),
    authorization: str = Header(...),
) -> HolidaysResponse:
    """Retrieve holidays for a given year."""
    try:
        return await client.get_holidays(year, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/leaves", response_model=LeavesResponse)
async def leaves(
    fy_id: str = Query(..., alias="fyId"),
    authorization: str = Header(...),
) -> LeavesResponse:
    """Retrieve leave entries for the provided financial year identifier."""
    try:
        return await client.get_leaves(fy_id, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/leaves/apply", response_model=ApplyLeaveResponse)
async def apply_leave(
    body: ApplyLeaveRequest,
    authorization: str = Header(...),
) -> ApplyLeaveResponse:
    """Apply for a leave or comp-off."""
    try:
        return await client.apply_leave(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/leaves/apply/comp-off", response_model=ApplyLeaveResponse)
async def apply_comp_off(body: ApplyCompOffRequest, authorization: str = Depends(auth_header_getter)):
    client = LeavesClient()
    return await client.apply_comp_off(body, authorization)

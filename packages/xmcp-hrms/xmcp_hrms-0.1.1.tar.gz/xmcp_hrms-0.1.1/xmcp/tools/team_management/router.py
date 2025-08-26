from fastapi import APIRouter, Header, HTTPException, Query
import httpx

from .client import TeamManagementClient
from .models import TeamLedgerResponse

router = APIRouter(prefix="/team-management")
client = TeamManagementClient()


@router.get("/ledger", response_model=TeamLedgerResponse)
async def team_ledger(
    empId: str = Query(...),
    fy: str = Query(...),
    authorization: str = Header(...),
) -> TeamLedgerResponse:
    """Retrieve leave/comp-off ledger for a team member."""
    try:
        return await client.get_team_ledger(empId, fy, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

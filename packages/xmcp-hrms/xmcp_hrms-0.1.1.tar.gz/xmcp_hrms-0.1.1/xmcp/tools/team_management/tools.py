from __future__ import annotations

"""Tools for team management endpoints."""

from typing import Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

import xmcp.tools.base as tools_base

ToolSpec = tools_base.ToolSpec


class TeamLedgerInput(BaseModel):
    empId: str = Field(..., description="Employee identifier of team member")
    fy: str = Field(..., description="Financial year range, e.g. 2025-2026")


def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    """Create tool specifications for team management APIs."""

    http_client = client or httpx.Client(base_url=base_url)

    def _get_team_ledger(empId: str, fy: str) -> dict:
        response = http_client.get(
            "/team-management/ledger",
            params={"empId": empId, "fy": fy},
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    return [
        ToolSpec(
            name="get_team_ledger",
            description="Fetch leave/comp-off ledger for a team member.",
            args_schema=TeamLedgerInput,
            func=_get_team_ledger,
        )
    ]


def create_langchain_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain StructuredTool instances for team management APIs."""

    specs = create_tool_specs(base_url, auth_header_getter, client)
    return [
        StructuredTool.from_function(
            func=spec.func,
            name=spec.name,
            description=spec.description,
            args_schema=spec.args_schema,
        )
        for spec in specs
    ]

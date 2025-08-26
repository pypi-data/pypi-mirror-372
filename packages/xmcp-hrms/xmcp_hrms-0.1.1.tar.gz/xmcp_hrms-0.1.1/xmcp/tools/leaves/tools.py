# src/xmcp/leaves/tools.py
from __future__ import annotations
"""Tools for interacting with leave-related MCP server endpoints."""

from typing import Any, Dict, Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from datetime import date
from pydantic import BaseModel, Field, ConfigDict

import xmcp.tools.base as tools_base
import xmcp.tools.leaves.models as leaves_models

ToolSpec = tools_base.ToolSpec
ApplyLeaveRequest = leaves_models.ApplyLeaveRequest
ApplyCompOffRequest = leaves_models.ApplyCompOffRequest


# ---- Input models for tools in this module ----

class HolidaysInput(BaseModel):
    """Input schema for the get_holidays tool.
    Accepts LeaveDate from the MCP client and derives the year."""
    # The MCP client sends "LeaveDate"; we alias to a Pythonic field name.
    leaveDate: date = Field(
        ...,
        alias="LeaveDate",
        description=(
            "Date of the leave (YYYY-MM-DD or ISO8601). The tool extracts the year and "
            "fetches holidays for that calendar year."
        ),
    )
    # Allow population by alias (LeaveDate) or field name (leaveDate), ignore extra keys.
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class LeavesInput(BaseModel):
    """Input schema for the get_leaves tool."""
    fyId: str = Field(..., description="Financial year identifier (e.g., '2025-26')")


# ---- Tool factory ----

def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    """
    Create framework-agnostic tool specifications for leave APIs.
    We call router paths like /holidays, /leaves, /leaves/apply, /leaves/apply/comp-off.
    """
    base = base_url.rstrip("/")
    http_client = client or httpx.Client(base_url=base, timeout=30.0)

    def _get_holidays(leaveDate: date) -> dict:
        year = leaveDate.year
        r = http_client.get(
             "/holidays",
             params={"year": year},
             headers={"Authorization": auth_header_getter()},
         )
        r.raise_for_status()
        return r.json()

    def _get_leaves(fyId: str) -> dict:
        r = http_client.get(
            "/leaves",
            params={"fyId": fyId},
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    def _apply_leave(**payload: dict) -> dict:
        req = ApplyLeaveRequest(**payload)
        r = http_client.post(
            "/leaves/apply",
            json=req.model_dump(mode="json"),  # date -> "YYYY-MM-DD"
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    def _apply_comp_off(**payload: dict) -> dict:
        # NOTE: comp-off has its own schema (compOffCount, workingDate, description)
        req = ApplyCompOffRequest(**payload)
        r = http_client.post(
            "/leaves/apply/comp-off",
            json=req.model_dump(mode="json"),
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    return [
        ToolSpec(
            name="get_holidays",
            description=(
                "Fetch holidays for the calendar year inferred from the provided LeaveDate."
            ),
            args_schema=HolidaysInput,
            func=_get_holidays,
        ),
        ToolSpec(
            name="get_leaves",
            description="Fetch leave records for a financial year.",
            args_schema=LeavesInput,
            func=_get_leaves,
        ),
        ToolSpec(
            name="apply_leave",
            description="Apply for a leave (category 'Leave' or 'Comp-Off').",
            args_schema=ApplyLeaveRequest,
            func=_apply_leave,
        ),
        ToolSpec(
            name="apply_comp_off",
            description="Apply for a comp-off credit.",
            args_schema=ApplyCompOffRequest,   # <-- important: correct schema
            func=_apply_comp_off,
        ),
    ]


def create_langchain_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain StructuredTool instances for leave APIs."""
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

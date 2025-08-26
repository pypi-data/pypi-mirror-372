from __future__ import annotations

"""Tools for miscellaneous endpoints."""

from typing import Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

import xmcp.tools.base as tools_base

ToolSpec = tools_base.ToolSpec


class EmployeeIdInput(BaseModel):
    employee_id: str = Field(..., description="Employee identifier")


class EmptyInput(BaseModel):
    """Schema for endpoints that require no parameters."""

    pass


def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    """Create tool specifications for miscellaneous APIs."""

    http_client = client or httpx.Client(base_url=base_url)

    def _health() -> dict:
        response = http_client.get("/health")
        response.raise_for_status()
        return response.json()

    def _get_financial_years() -> dict:
        response = http_client.get(
            "/financial-years",
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    def _get_employee_profile(employee_id: str) -> dict:
        response = http_client.get(
            f"/employees/{employee_id}",
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    return [
        ToolSpec(
            name="health",
            description="Check server health status.",
            args_schema=EmptyInput,
            func=_health,
        ),
        ToolSpec(
            name="get_financial_years",
            description="Fetch financial year data for the current employee.",
            args_schema=EmptyInput,
            func=_get_financial_years,
        ),
        ToolSpec(
            name="get_employee_profile",
            description="Fetch HRMS profile for an employee by ID.",
            args_schema=EmployeeIdInput,
            func=_get_employee_profile,
        ),
    ]


def create_langchain_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain StructuredTool instances for miscellaneous APIs."""

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

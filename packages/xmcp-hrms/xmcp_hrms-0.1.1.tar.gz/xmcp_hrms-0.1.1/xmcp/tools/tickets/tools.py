from __future__ import annotations

"""Tools for interacting with ticket endpoints."""

from typing import Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

import xmcp.tools.base as tools_base

ToolSpec = tools_base.ToolSpec


class TicketsInput(BaseModel):
    id: str = Field(..., description="Employee identifier")
    status: str = Field(..., description="Ticket status to filter")
    page: int = Field(1, description="Page number", ge=1)


class SubmitTicketInput(BaseModel):
    """Input for submitting a ticket."""

    id: str = Field(..., description="Identifier of the ticket to submit")


class EmptyInput(BaseModel):
    """Schema for endpoints that require no parameters."""

    pass


def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    """Create tool specifications for ticket APIs."""

    http_client = client or httpx.Client(base_url=base_url)

    def _get_tickets(id: str, status: str, page: int = 1) -> dict:
        response = http_client.get(
            "/tickets/my",
            params={"id": id, "status": status, "page": page},
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    def _raise_ticket() -> dict:
        response = http_client.post(
            "/tickets/draft",
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    def _submit_ticket(id: str) -> dict:
        response = http_client.post(
            "/tickets/submit",
            params={"id": id},
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    return [
        ToolSpec(
            name="get_tickets",
            description="Fetch tickets for the current employee.",
            args_schema=TicketsInput,
            func=_get_tickets,
        ),
        ToolSpec(
            name="raise_ticket",
            description="Create a new ticket draft.",
            args_schema=EmptyInput,
            func=_raise_ticket,
        ),
        ToolSpec(
            name="submit_ticket",
            description="Submit a draft ticket.",
            args_schema=SubmitTicketInput,
            func=_submit_ticket,
        ),
    ]


def create_langchain_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain StructuredTool instances for ticket APIs."""

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

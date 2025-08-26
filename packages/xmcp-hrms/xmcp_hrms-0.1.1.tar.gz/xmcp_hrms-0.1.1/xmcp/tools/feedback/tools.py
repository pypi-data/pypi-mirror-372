from __future__ import annotations

"""Tools for interacting with feedback endpoints."""

from typing import Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

import xmcp.tools.base as tools_base
import xmcp.tools.feedback.models as feedback_models

ToolSpec = tools_base.ToolSpec
AddFeedbackRequest = feedback_models.AddFeedbackRequest


class RMFeedbacksInput(BaseModel):
    """Input for retrieving RM feedback entries."""

    id: Optional[str] = Field(
        None, description="Employee identifier to filter feedbacks"
    )


class EmptyInput(BaseModel):
    """Schema for endpoints that require no parameters."""

    pass


def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    """Create tool specifications for feedback APIs."""

    http_client = client or httpx.Client(base_url=base_url)

    def _add_feedback(**payload: dict) -> dict:
        req = AddFeedbackRequest(**payload)
        response = http_client.post(
            "/feedback/add",
            json=req.model_dump(mode="json"),
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    def _rm_feedbacks(id: Optional[str] = None) -> dict:
        params = {"id": id} if id else {}
        response = http_client.get(
            "/feedback/rm-feedbacks",
            params=params,
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    def _feedback_levels() -> dict:
        response = http_client.get(
            "/feedback/levels",
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    return [
        ToolSpec(
            name="add_feedback",
            description="Submit feedback for a team member.",
            args_schema=AddFeedbackRequest,
            func=_add_feedback,
        ),
        ToolSpec(
            name="get_rm_feedbacks",
            description="Retrieve RM feedback entries for an employee.",
            args_schema=RMFeedbacksInput,
            func=_rm_feedbacks,
        ),
        ToolSpec(
            name="get_feedback_levels",
            description="List users available in feedback levels.",
            args_schema=EmptyInput,
            func=_feedback_levels,
        ),
    ]


def create_langchain_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain StructuredTool instances for feedback APIs."""

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

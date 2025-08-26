from __future__ import annotations

from typing import Any, Dict, List, Tuple
import json
import os

import httpx
from fastapi import APIRouter, Body, HTTPException, Request, status
from pydantic import BaseModel, ValidationError

import xmcp.tool_registry as tool_registry
import xmcp.auth_context as auth_context

all_tool_specs = tool_registry.all_tool_specs
set_request_headers = auth_context.set_request_headers
auth_header_getter = auth_context.auth_header_getter

router = APIRouter(prefix="/mcp-compat", tags=["mcp-compat"])


# ---- Helpers ----

def _load_specs(request: Request):
    """
    Build ToolSpecs with the current request headers bound, so tools can
    propagate Authorization (or other) headers via auth_header_getter().
    """
    set_request_headers(dict(request.headers))
    base =  ("http://localhost:8000").rstrip("/")
    return list(all_tool_specs(base, auth_header_getter))


def _by_exact_name(specs) -> Dict[str, Any]:
    return {s.name: s for s in specs}


# ---- Models ----

class InvokeBody(BaseModel):
    """
    Unified body: supports both payload styles on both endpoints.
      - /invoke: { "name": "tool_name", "arguments": {...} }
      - /call:   { "tool": "tool_name", "args": {...} }
    """
    name: str | None = None
    arguments: Dict[str, Any] | None = None
    tool: str | None = None
    args: Dict[str, Any] | None = None

    def pick(self) -> Tuple[str, Dict[str, Any]]:
        tool_name = self.name or self.tool
        if not tool_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Missing 'name' (for /invoke) or 'tool' (for /call')",
            )
        tool_args = self.arguments if self.arguments is not None else self.args
        if tool_args is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Missing 'arguments' (for /invoke) or 'args' (for /call')",
            )
        return tool_name, tool_args


# ---- Routes ----

@router.get("/tools")
def list_tools(request: Request):
    specs = _load_specs(request)
    out: List[Dict[str, Any]] = [
        {"name": "ping", "description": "health check", "args_schema": None}
    ]
    for s in specs:
        schema = None
        if getattr(s, "args_schema", None):
            try:
                schema = s.args_schema.model_json_schema()
            except Exception:
                # Fallback minimal schema
                schema = {"title": getattr(s.args_schema, "__name__", "Args")}
        out.append(
            {"name": s.name, "description": getattr(s, "description", ""), "args_schema": schema}
        )
    return {"tools": out}


def _execute(spec, args: Dict[str, Any]):
    # Validate args against the tool's schema if present
    if getattr(spec, "args_schema", None):
        try:
            args = spec.args_schema(**args).model_dump()
        except ValidationError as e:
            # Clean 422 with pydantic error details
            raise HTTPException(status_code=422, detail=json.loads(e.json()))
    # Call the tool function (sync in your codebase)
    try:
        return spec.func(**args)
    except httpx.HTTPStatusError as exc:
        # Map backend status + JSON detail when available
        detail: Any = exc.response.text
        try:
            data = exc.response.json()
        except ValueError:
            pass
        else:
            if isinstance(data, dict) and "detail" in data:
                detail = data["detail"]
            else:
                detail = data
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/invoke")
def invoke_tool(body: InvokeBody = Body(...), request: Request = None):
    if request is not None:
        set_request_headers(dict(request.headers))
    # Built-in ping
    if (body.name or body.tool) == "ping":
        return {"result": "pong"}

    name, args = body.pick()
    specs = _by_exact_name(_load_specs(request))
    spec = specs.get(name)
    if not spec:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Tool '{name}' not found", "available_tools": sorted(specs.keys())},
        )
    return {"result": _execute(spec, args)}


@router.post("/call")
def call_tool(body: InvokeBody = Body(...), request: Request = None):
    # Identical behavior to /invoke; accepts either payload style
    return invoke_tool(body, request)

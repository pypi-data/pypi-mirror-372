from __future__ import annotations
import os
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
import xmcp.tool_registry as tool_registry
import xmcp.auth_context as auth_context

all_tool_specs = tool_registry.all_tool_specs
auth_header_getter = auth_context.auth_header_getter

def build_xmcp() -> FastMCP:
    mcp = FastMCP("XAgent HR MCP", stateless_http=True)

    # Tiny health tool
    @mcp.tool(name="ping", description="health check")
    def ping() -> str:
        return "pong"

    # Where your tools should call (usually your own FastAPI, not HRMS directly)
    base_url = ("http://localhost:8000").rstrip("/")

    specs = list(all_tool_specs(base_url, auth_header_getter))
    print(f"[mcp] Registering {len(specs)} ToolSpecs…")

    for spec in specs:
        def _register(s):
            @mcp.tool(name=s.name, description=s.description or s.name)
            def tool(params: Dict[str, Any] | None = None) -> Any:
                params = params or {}
                if getattr(s, "args_schema", None):
                    model = s.args_schema(**params)  # validate/coerce
                    return s.func(**model.model_dump())
                return s.func(**params)
        _register(spec)

    return mcp

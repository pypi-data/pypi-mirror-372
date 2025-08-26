# src/xmcp/main.py
from fastapi import FastAPI, Request
import xmcp.mcp_runtime as mcp_runtime
import xmcp.auth_context as auth_context
import xmcp.compat_rest as compat_rest
import xmcp.tools.leaves.router as leaves_router_module
import xmcp.tools.attendance.router as attendance_router_module
import xmcp.tools.feedback.router as feedback_router_module
import xmcp.tools.tickets.router as tickets_router_module
import xmcp.tools.team_management.router as team_router_module
import xmcp.tools.miscellaneous.router as misc_router_module
import xmcp.tools.referrals.router as referrals_router_module

build_xmcp = mcp_runtime.build_xmcp
set_request_headers = auth_context.set_request_headers
compat_router = compat_rest.router
leaves_router = leaves_router_module.router
leaves_client = leaves_router_module.client
attendance_router = attendance_router_module.router
attendance_client = attendance_router_module.client
feedback_router = feedback_router_module.router
feedback_client = feedback_router_module.client
tickets_router = tickets_router_module.router
tickets_client = tickets_router_module.client
team_router = team_router_module.router
team_client = team_router_module.client
misc_router = misc_router_module.router
misc_client = misc_router_module.client
referrals_router = referrals_router_module.router
referrals_client = referrals_router_module.client

app = FastAPI(title="XAgent HR MCP Host")

# Put headers into a contextvar so tools (or compat) can read them
@app.middleware("http")
async def _stash_headers(request: Request, call_next):
    # capture for both /mcp (real MCP) and /mcp-compat (Postman/curl shim)
    if request.url.path.startswith("/mcp") or request.url.path.startswith("/mcp-compat"):
        set_request_headers(dict(request.headers))
    return await call_next(request)

# Mount MCP server (streamable HTTP → HTTP → SSE)
mcp = build_xmcp()
mounted = False
for method in ("streamable_http_app", "http_app", "sse_app"):
    mount = getattr(mcp, method, None)
    if callable(mount):
        app.mount("/mcp", mount())
        print(f"[mcp] Mounted {method} at /mcp")
        mounted = True
        break
if not mounted:
    raise RuntimeError("FastMCP has no HTTP/SSE mount; upgrade `mcp` package.")

# Register domain routers so endpoints like /holidays or /leaves exist
app.include_router(misc_router)
app.include_router(leaves_router)
app.include_router(attendance_router)
app.include_router(feedback_router)
app.include_router(tickets_router)
app.include_router(team_router)
app.include_router(referrals_router)

# Expose HRMS clients for tests to monkeypatch
client = leaves_client
# Others are available as attendance_client, feedback_client, tickets_client, team_client, misc_client, referrals_client

# Optional REST shim for Postman/curl sanity checks
app.include_router(compat_router)

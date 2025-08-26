"""Public package API for xmcp.

This module re-exports commonly used helpers so callers can import them
from ``xmcp`` without digging through internal modules.
"""

import xmcp.mcp_runtime as mcp_runtime
import xmcp.tool_registry as tool_registry
import xmcp.tools as tools_module
import xmcp.auth_context as auth_context

build_xmcp = mcp_runtime.build_xmcp
all_tool_specs = tool_registry.all_tool_specs
create_tool_specs = tools_module.create_tool_specs
create_langchain_tools = tools_module.create_langchain_tools
set_request_headers = auth_context.set_request_headers
auth_header_getter = auth_context.auth_header_getter

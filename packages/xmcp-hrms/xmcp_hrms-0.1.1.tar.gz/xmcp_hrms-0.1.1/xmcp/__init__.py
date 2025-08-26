"""Top-level package for xmcp.

Re-exports the most commonly used helpers for convenience so users can
simply ``import xmcp`` and access the public API.
"""

import xmcp.api as api

build_xmcp = api.build_xmcp
all_tool_specs = api.all_tool_specs
create_tool_specs = api.create_tool_specs
create_langchain_tools = api.create_langchain_tools
set_request_headers = api.set_request_headers
auth_header_getter = api.auth_header_getter

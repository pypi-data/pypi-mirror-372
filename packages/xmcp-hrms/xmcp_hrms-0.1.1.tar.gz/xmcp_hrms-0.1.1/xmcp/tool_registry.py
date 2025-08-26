
from typing import Callable, List, Optional
import httpx

import xmcp.tools.leaves.tools as leaves_tools
import xmcp.tools.attendance.tools as attendance_tools
import xmcp.tools.feedback.tools as feedback_tools
import xmcp.tools.tickets.tools as tickets_tools
import xmcp.tools.team_management.tools as team_tools
import xmcp.tools.miscellaneous.tools as misc_tools

try:
    import xmcp.tools.referrals.tools as referrals_tools
except Exception:
    referrals_tools = None

_leaves = leaves_tools.create_tool_specs
_attendance = attendance_tools.create_tool_specs
_feedback = feedback_tools.create_tool_specs
_tickets = tickets_tools.create_tool_specs
_team = team_tools.create_tool_specs
_misc = misc_tools.create_tool_specs
_referrals = referrals_tools.create_tool_specs if referrals_tools else None

def all_tool_specs(base_url: str, auth_header_getter: Callable[[], str], http_client: Optional[httpx.Client] = None):
    specs = []
    for factory in (_leaves, _attendance, _feedback, _tickets, _team, _misc):
        specs.extend(factory(base_url, auth_header_getter, client=http_client))
    if _referrals:
        specs.extend(_referrals(base_url, auth_header_getter, client=http_client))
    # de-duplicate by name
    seen = set(); out = []
    for s in specs:
        if s.name not in seen:
            out.append(s); seen.add(s.name)
    return out

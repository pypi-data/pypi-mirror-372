
from __future__ import annotations
from typing import Callable, List, Optional
import httpx
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
import xmcp.tools.base as tools_base

ToolSpec = tools_base.ToolSpec

class HoursRequest(BaseModel):
    startTime: str = Field(..., description="HH:MM (24h)")
    endTime: str = Field(..., description="HH:MM (24h)")

class FillTimingsRequest(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")

def _hhmm_to_minutes(s: str) -> int:
    h, m = [int(x) for x in s.split(":")]
    return h*60 + m

def create_tool_specs(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None) -> List[ToolSpec]:
    http_client = client or httpx.Client(base_url=base_url, timeout=20.0)

    def _calculate_hours(startTime: str, endTime: str) -> dict:
        total = max(0, _hhmm_to_minutes(endTime) - _hhmm_to_minutes(startTime))
        return {"actualHours": round(total/60.0, 2)}

    def _fill_from_ipad(date: str) -> dict:
        r = http_client.get(
            "/api/v2/attendance/attendances/employee/attendance-date",
            params={"attendanceDate": date},
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        data = r.json()
        # Heuristic: extract earliest "in" and latest "out"
        ins = []; outs = []
        for rec in data.get("records", data if isinstance(data, list) else []):
            t = (rec.get("type") or "").lower()
            if t == "in": ins.append(rec.get("time"))
            if t == "out": outs.append(rec.get("time"))
        if not ins or not outs:
            return {"startTime": None, "endTime": None, "message": "No device timings found"}
        return {"startTime": min(ins), "endTime": max(outs)}

    return [
        ToolSpec("calculate_attendance_hours", "Compute hours from start and end time.", HoursRequest, _calculate_hours),
        ToolSpec("fill_arr_timings_from_ipad", "Attempt to fill start/end from device logs for a given date.", FillTimingsRequest, _fill_from_ipad),
    ]

def create_langchain_tools(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None):
    specs = create_tool_specs(base_url, auth_header_getter, client)
    return [StructuredTool.from_function(func=s.func, name=s.name, description=s.description, args_schema=s.args_schema) for s in specs]

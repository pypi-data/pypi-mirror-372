from __future__ import annotations
from typing import Callable, List, Optional
import httpx
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
import xmcp.tools.base as tools_base

ToolSpec = tools_base.ToolSpec

class AttendanceInput(BaseModel):
    year: int
    month: int

class AttendanceDateInput(BaseModel):
    attendanceDate: str

class ArrListInput(BaseModel):
    year: int
    month: int
    page: int = 1

class SubmitArrInput(BaseModel):
    employeeId: str
    attendanceDate: str
    reasonProvidedByEmployee: str
    issueType: str
    startTime: str | None = None
    endTime: str | None = None
    actualHours: str | None = None
    projectId: str | None = None
    description: str | None = None
    file_path: str | None = Field(None, description="Optional local file path to attach")

class ApplyLeaveInput(BaseModel):
    # Align this payload to your Postman body keys
    leaveType: str = Field("Debit", description='Leave type; defaults to "Debit".')
    leaveCount: int
    leaveDate: str | list[str]
    comments: str | None = None

def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    http_client = client or httpx.Client(base_url=base_url, timeout=20.0)

    def _get_attendance(year: int, month: int) -> dict:
        r = http_client.post(
            "/attendance/my-attendance",
            params={"year": year, "month": month},
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    def _get_attendance_date(attendanceDate: str) -> dict:
        r = http_client.get(
            "/api/v2/attendance/attendances/employee/attendance-date",
            params={"attendanceDate": attendanceDate},
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    def _list_arrs(year: int, month: int, page: int = 1) -> dict:
        r = http_client.get(
            "/api/v2/attendance/attendances/my-regularized-attendance",
            params={"year": year, "month": month, "page": page},
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    def _submit_arr(**kwargs) -> dict:
        file_path = kwargs.pop("file_path", None)
        employeeId = kwargs.pop("employeeId")
        data = {k: v for k, v in kwargs.items() if v is not None}
        files = None
        if file_path:
            files = {
                "file": (
                    file_path.split("/")[-1],
                    open(file_path, "rb"),
                    "application/octet-stream",
                )
            }
            data.pop("file", None)
        r = http_client.post(
            "/api/v2/attendance/attendances/regularisation/project",
            params={"employeeId": employeeId},  # proxy param -> router maps to Id
            data={"employeeId": employeeId, **data},  # router expects form-data
            files=files,
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    def _apply_leave(**payload) -> dict:
        r = http_client.post(
            "/api/v2/attendance/leaves/apply",
            json=payload,
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    return [
        ToolSpec("get_attendance", "Get attendance entries for a month.", AttendanceInput, _get_attendance),
        ToolSpec("get_attendance_date", "Get iPad-marked timings for a date.", AttendanceDateInput, _get_attendance_date),
        ToolSpec("list_arrs", "List attendance regularization requests (ARRs).", ArrListInput, _list_arrs),
        ToolSpec("submit_arr", "Submit an ARR (supports file).", SubmitArrInput, _submit_arr),
        ToolSpec("apply_leave", "Apply for a leave (v2).", ApplyLeaveInput, _apply_leave),
    ]

def create_langchain_tools(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None):
    specs = create_tool_specs(base_url, auth_header_getter, client)
    return [
        StructuredTool.from_function(
            func=s.func, name=s.name, description=s.description, args_schema=s.args_schema
        )
        for s in specs
    ]

# --- ADD/REPLACE IN attendance/router.py ---

from fastapi import APIRouter, Header, HTTPException, Query, UploadFile, File, Form, Body
import httpx
from .client import AttendanceClient
from .models import AttendanceResponse

router = APIRouter(tags=["attendance"])
client = AttendanceClient()

@router.post("/attendance/my-attendance", response_model=AttendanceResponse)
async def my_attendance(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    authorization: str = Header(...),
) -> AttendanceResponse:
    try:
        return await client.get_my_attendance(year, month, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.get("/api/v2/attendance/attendances/employee/attendance-date")
async def attendance_date(
    attendanceDate: str = Query(...),
    authorization: str = Header(...),
) -> dict:
    try:
        return await client.get_attendance_date(attendanceDate, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.get("/api/v2/attendance/attendances/my-regularized-attendance")
async def my_regularized_attendance(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    page: int = Query(1, ge=1),
    authorization: str = Header(...),
) -> dict:
    try:
        return await client.list_arrs(year, month, page, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.post("/api/v2/attendance/attendances/regularisation/project")
async def submit_arr(
    employeeId: str = Query(..., description="HRMS employee Id, as 'Id' query for HRMS"),
    attendanceDate: str = Form(...),
    reasonProvidedByEmployee: str = Form(...),
    issueType: str = Form(...),
    startTime: str | None = Form(None),
    endTime: str | None = Form(None),
    actualHours: str | None = Form(None),
    projectId: str | None = Form(None),
    description: str | None = Form(None),
    file: UploadFile | None = File(None),
    authorization: str = Header(...),
) -> dict:
    try:
        payload = {
            "attendanceDate": attendanceDate,
            "reasonProvidedByEmployee": reasonProvidedByEmployee,
            "issueType": issueType,
            "startTime": startTime,
            "endTime": endTime,
            "actualHours": actualHours,
            "projectId": projectId,
            "description": description,
            "file": "null" if file is None else None,
        }
        payload = {k: v for k, v in payload.items() if v not in (None, "")}
        file_tuple = None
        if file is not None:
            content = await file.read()
            file_tuple = (
                file.filename,
                content,
                file.content_type or "application/octet-stream",
            )
        return await client.submit_arr(employeeId, payload, authorization, file_tuple)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.post("/api/v2/attendance/leaves/apply")
async def apply_leave(
    body: dict = Body(...),
    authorization: str = Header(...),
) -> dict:
    try:
        return await client.apply_leave(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

import os
import httpx
from dotenv import load_dotenv
load_dotenv()

class AttendanceClient:
    def __init__(self, base_url: str | None = None, timeout: float = 20.0) -> None:
        self.base_url = base_url or os.getenv("HRMS_API_BASE_URL")
        if not self.base_url:
            raise RuntimeError("HRMS_API_BASE_URL is not configured")
        self.timeout = timeout

    async def get_my_attendance(self, year: int, month: int, auth_header: str) -> dict:
        params = {"year": year, "month": month}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/attendance/my-attendance",
                params=params,
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()

    async def get_attendance_date(self, attendance_date: str, auth_header: str) -> dict:
        params = {"attendanceDate": attendance_date}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/v2/attendance/attendances/employee/attendance-date",
                params=params,
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()

    async def list_arrs(self, year: int, month: int, page: int, auth_header: str) -> dict:
        params = {"year": year, "month": month, "page": page}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/v2/attendance/attendances/my-regularized-attendance",
                params=params,
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()

    async def submit_arr(
        self,
        employee_id: str,
        form_data: dict,
        auth_header: str,
        file_tuple: tuple | None = None,
    ) -> dict:
        params = {"Id": employee_id}
        files = None
        data = form_data
        if file_tuple:
            files = {"file": file_tuple}
            # HRMS ignores "file": "null" when a real file is present
            data = {k: v for k, v in form_data.items() if k != "file"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/v2/attendance/attendances/regularisation/project",
                params=params,
                data=data,
                files=files,
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()

    async def apply_leave(self, payload: dict, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/v2/attendance/leaves/apply",
                json=payload,
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()


import os
import httpx
from dotenv import load_dotenv
load_dotenv()

class ReferralsClient:
    def __init__(self, base_url: str | None = None, timeout: float = 20.0) -> None:
        self.base_url = base_url or os.getenv("HRMS_API_BASE_URL")
        if not self.base_url:
            raise RuntimeError("HRMS_API_BASE_URL is not configured")
        self.timeout = timeout

    async def search_openings(self, body: dict, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/api/v2/elastic/es/search/All_Openings", json=body, headers={"Authorization": auth_header})
            r.raise_for_status(); return r.json()

    async def add_candidate(self, body: dict, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/api/v2/hr/candidates/add", json=body, headers={"Authorization": auth_header})
            r.raise_for_status(); return r.json()

    async def upload_resume(self, candidate_id: str, file_tuple, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.put(f"{self.base_url}/api/v2/hr/candidates/updateProfile", params={"Id": candidate_id}, files={"file": file_tuple}, headers={"Authorization": auth_header})
            r.raise_for_status(); return r.json()

    async def create_application(self, body: dict, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/api/v2/hr/applications", json=body, headers={"Authorization": auth_header})
            r.raise_for_status(); return r.json()

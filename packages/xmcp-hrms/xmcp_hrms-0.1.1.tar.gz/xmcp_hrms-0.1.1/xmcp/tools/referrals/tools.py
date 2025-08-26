
from __future__ import annotations
from typing import Callable, List, Optional, Dict, Any
import httpx
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
import xmcp.tools.base as tools_base

ToolSpec = tools_base.ToolSpec

class OpeningsToolInput(BaseModel):
    page: int = 1
    pageSize: int = 10
    filters: List[Dict[str, Any]] = Field(default_factory=list)

class CandidatePayload(BaseModel):
    payload: Dict[str, Any]

class ApplicationPayload(BaseModel):
    payload: Dict[str, Any]

class UploadResumeInput(BaseModel):
    candidate_id: str
    file_path: str

def create_tool_specs(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None) -> List[ToolSpec]:
    http_client = client or httpx.Client(base_url=base_url, timeout=20.0)

    def _search_openings(page: int = 1, pageSize: int = 10, filters: List[Dict[str, Any]] = None) -> dict:
        body = {"name": "All_Openings", "index": "openings", "page": page, "pageSize": pageSize, "filters": filters or []}
        r = http_client.post("/api/v2/elastic/es/search/All_Openings", json=body, headers={"Authorization": auth_header_getter()})
        r.raise_for_status(); return r.json()

    def _add_candidate(payload: dict) -> dict:
        r = http_client.post("/api/v2/hr/candidates/add", json=payload, headers={"Authorization": auth_header_getter()})
        r.raise_for_status(); return r.json()

    def _upload_candidate_resume(candidate_id: str, file_path: str) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.split("/")[-1], f, "application/octet-stream")}
            r = http_client.put(f"/api/v2/hr/candidates/updateProfile", params={"Id": candidate_id}, files=files, headers={"Authorization": auth_header_getter()})
            r.raise_for_status(); return r.json()

    def _create_application(payload: dict) -> dict:
        r = http_client.post("/api/v2/hr/applications", json=payload, headers={"Authorization": auth_header_getter()})
        r.raise_for_status(); return r.json()

    return [
        ToolSpec("search_openings", "Search current job openings (ES).", OpeningsToolInput, _search_openings),
        ToolSpec("add_candidate", "Add a candidate profile.", CandidatePayload, _add_candidate),
        ToolSpec("upload_candidate_resume", "Upload a resume for candidate Id.", UploadResumeInput, _upload_candidate_resume),
        ToolSpec("create_application", "Create a job application for a candidate.", ApplicationPayload, _create_application),
    ]

def create_langchain_tools(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None):
    specs = create_tool_specs(base_url, auth_header_getter, client)
    return [StructuredTool.from_function(func=s.func, name=s.name, description=s.description, args_schema=s.args_schema) for s in specs]

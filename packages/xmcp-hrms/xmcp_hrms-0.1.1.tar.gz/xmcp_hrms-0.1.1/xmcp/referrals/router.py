
from fastapi import APIRouter, Header, HTTPException, UploadFile, File, Query, Body
import httpx
from .client import ReferralsClient

router = APIRouter(prefix="/api/v2")

client = ReferralsClient()

@router.post("/elastic/es/search/All_Openings")
async def search_openings(body: dict = Body(...), authorization: str = Header(...)) -> dict:
    try:
        return await client.search_openings(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.post("/hr/candidates/add")
async def add_candidate(body: dict = Body(...), authorization: str = Header(...)) -> dict:
    try:
        return await client.add_candidate(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.put("/hr/candidates/updateProfile")
async def upload_resume(Id: str = Query(...), file: UploadFile = File(...), authorization: str = Header(...)) -> dict:
    try:
        content = await file.read()
        return await client.upload_resume(Id, (file.filename, content, file.content_type or "application/octet-stream"), authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.post("/hr/applications")
async def create_application(body: dict = Body(...), authorization: str = Header(...)) -> dict:
    try:
        return await client.create_application(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

from __future__ import annotations
from contextvars import ContextVar
import os
from typing import Dict

_request_headers: ContextVar[Dict[str, str]] = ContextVar("_request_headers", default={})

def set_request_headers(h: Dict[str, str]) -> None:
    _request_headers.set({k.lower(): v for k, v in h.items()})

def get_bearer() -> str:
    h = _request_headers.get({})
    token = h.get("authorization") or h.get("x-authorization") or os.getenv("DEFAULT_AUTHORIZATION", "")
    return token

def auth_header_getter() -> str:
    return get_bearer()

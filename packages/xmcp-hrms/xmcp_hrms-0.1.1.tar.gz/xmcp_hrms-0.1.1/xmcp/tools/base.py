from dataclasses import dataclass
from typing import Any, Callable, Type

from pydantic import BaseModel


@dataclass
class ToolSpec:
    """Framework-agnostic definition of a tool."""

    name: str
    description: str
    args_schema: Type[BaseModel]
    func: Callable[..., Any]

from fastapi import HTTPException
from enum import Enum
from typing import TypeVar, Optional

T = TypeVar("T", bound=Enum)

class CustomHTTPException(HTTPException):
    def __init__(self, error_code: T, detail: Optional[str] = None) -> None: ...

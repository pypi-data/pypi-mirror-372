from fastapi import HTTPException
from enum import Enum
from typing import TypeVar, Optional

T = TypeVar("T", bound=Enum)


class CustomHTTPException(HTTPException):
    def __init__(self, error_code: T, detail: Optional[str] = None):
        super().__init__(status_code=getattr(error_code, "status_code", 500),
                         detail=detail or getattr(error_code, "detail", "Unknown error"))
        self.error_code = error_code

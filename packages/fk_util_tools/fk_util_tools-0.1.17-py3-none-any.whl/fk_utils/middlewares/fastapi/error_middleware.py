import traceback
from typing import Callable, Awaitable, Type, Any
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from fk_utils.exceptions.custom_http_exception import CustomHTTPException
from fastapi import Request, Response
from fk_utils.middlewares.fastapi.i18n import _
import uuid
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    VALIDATION_ERROR = (
        "MAIN-VAL-001",
        "Validation Error",
        422,
        "The input data is invalid.",
    )
    RESOURCE_NOT_FOUND = (
        "MAIN-VAL-002",
        "Resource Not Found",
        404,
        "The requested resource does not exist.",
    )
    SYSTEM_ERROR = (
        "MAIN-SYS-001",
        "System Error",
        500,
        "An unexpected error occurred.",
    )

    def __init__(self, error_code: str, title: str, status_code: int, detail: str):
        self.error_code = error_code
        self.title = title
        self.status_code = status_code
        self.detail = detail


class ErrorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, error_enum: Type[ErrorCode], **kwargs: Any) -> None:
        """
        Middleware to handle global errors in the application.

        :param app: FastAPI application.
        :param error_enum: Enumeration of error codes.
        """
        super().__init__(app, **kwargs)
        self.error_enum = error_enum

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            response = await call_next(request)
            return response
        except CustomHTTPException as custom_exc:
            return self.build_error_response(
                error_code=custom_exc.error_code,
                detail=custom_exc.detail,
                request=request,
            )
        except RequestValidationError as validation_exc:
            user_friendly_detail = self.format_validation_errors(validation_exc, request)
            return self.build_error_response(
                error_code=self.error_enum.VALIDATION_ERROR,
                detail=user_friendly_detail,
                request=request,
            )
        except StarletteHTTPException as http_exc:
            error_code = (
                self.error_enum.RESOURCE_NOT_FOUND
                if http_exc.status_code == 404
                else self.error_enum.VALIDATION_ERROR
            )
            return self.build_error_response(
                error_code=error_code,
                detail=str(http_exc.detail),
                request=request,
            )
        except Exception:
            return self.build_error_response(
                error_code=self.error_enum.SYSTEM_ERROR,
                detail="An unexpected error occurred.",
                request=request,
            )

    def build_error_response(self, error_code: ErrorCode, detail: str, request: Request) -> JSONResponse:
        """
        Builds a JSON response for errors.

        :param error_code: Error code.
        :param detail: Error detail.
        :param request: HTTP request.
        :return: JSON response with the formatted error.
        """
        instance_id = str(uuid.uuid4())
        translated_detail = _(detail, request) if isinstance(detail, str) else detail
        logger.error(
            f"Error: {error_code.error_code} - {error_code.title} - {translated_detail} - Instance: {instance_id} - Traceback: {traceback.format_exc()}"
        )
        return JSONResponse(
            status_code=error_code.status_code,
            content={
                "error_code": error_code.error_code,
                "title": _(error_code.title, request),
                "status": error_code.status_code,
                "detail": translated_detail,
                "instance": instance_id,
            },
        )

    def format_validation_errors(self, exc: RequestValidationError, request: Request) -> str:
        error_messages = []
        for error in exc.errors():
            loc = "".join(map(str, error.get("loc", []))).replace("body", "")
            msg = error.get("msg", "Invalid value")

            ctx = error.get("ctx")
            if ctx:
                ctx_details = ", ".join(f"{value}" for key, value in ctx.items())
                msg += f" {ctx_details}"

            error_messages.append(f"{_(msg, request)}: {loc}")

        return " | ".join(error_messages)

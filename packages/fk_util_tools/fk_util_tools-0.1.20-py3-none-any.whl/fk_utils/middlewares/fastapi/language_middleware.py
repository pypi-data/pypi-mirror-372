from typing import Awaitable, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
from fk_utils.middlewares.fastapi.i18n import set_locale


class LanguageMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, translation_dir: Path, redis_url: str, **kwargs):
        super().__init__(app, **kwargs)
        self.translation_dir = translation_dir
        self.redis_url = redis_url

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        await set_locale(request, self.translation_dir, self.redis_url)
        response = await call_next(request)
        return response

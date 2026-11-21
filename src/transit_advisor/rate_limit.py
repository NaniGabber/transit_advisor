from collections.abc import MutableMapping
from math import ceil
from time import monotonic

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class SourceRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        requests: int,
        window_seconds: float,
        trust_proxy_headers: bool = False,
    ) -> None:
        super().__init__(app)
        self.requests = requests
        self.window_seconds = window_seconds
        self.trust_proxy_headers = trust_proxy_headers
        self._windows: MutableMapping[str, tuple[float, int]] = {}

    def _source(self, request: Request) -> str:
        if self.trust_proxy_headers:
            forwarded = request.headers.get("x-forwarded-for")
            if forwarded:
                return forwarded.split(",", 1)[0].strip()

        if request.client is not None:
            return request.client.host
        return "unknown"

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        source = self._source(request)
        now = monotonic()

        expired_sources = [
            known_source
            for known_source, (window_started, _) in self._windows.items()
            if now - window_started >= self.window_seconds
        ]
        for known_source in expired_sources:
            del self._windows[known_source]

        window_started, request_count = self._windows.get(source, (now, 0))

        if now - window_started >= self.window_seconds:
            window_started = now
            request_count = 0

        request_count += 1
        retry_after = max(1, ceil(self.window_seconds - (now - window_started)))
        remaining = max(0, self.requests - request_count)

        if request_count > self.requests:
            self._windows[source] = (window_started, request_count)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                },
            )

        self._windows[source] = (window_started, request_count)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(retry_after)
        return response

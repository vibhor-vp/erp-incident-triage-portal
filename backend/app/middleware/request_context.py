"""Request context middleware (request_id + one structured request log line)."""

from __future__ import annotations

import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

from app.core.logging import reset_request_id, set_request_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid4())
        token = set_request_id(request_id)

        start = time.perf_counter()
        response = None
        raised: Exception | None = None

        try:
            response = await call_next(request)
            return response
        except Exception as exc:  # pragma: no cover
            raised = exc
            raise
        finally:
            latency_ms = round((time.perf_counter() - start) * 1000.0, 2)
            status_code = getattr(response, "status_code", 500)

            # Attach request id to response when possible.
            if response is not None:
                response.headers["X-Request-ID"] = request_id

            self._logger.info(
                "http_request",
                extra={
                    "event": "http_request",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "unhandled_exception": raised is not None,
                },
            )

            reset_request_id(token)

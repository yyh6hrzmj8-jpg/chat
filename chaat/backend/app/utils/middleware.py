import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("request")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info("%s %s -> %s (%.1fms)", request.method, request.url.path, getattr(response, "status_code", "?"), duration_ms)
        return response

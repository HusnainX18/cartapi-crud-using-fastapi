import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every incoming request and outgoing response with duration.
    Attach this to the FastAPI app in main.py.
    """

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        logger.info(
            f"--> REQUEST  {request.method} {request.url.path}"
            + (f"?{request.url.query}" if request.url.query else "")
        )

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"<-- RESPONSE {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration_ms}ms"
        )

        return response
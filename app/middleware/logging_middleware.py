import http
import json
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs one line per response with an explicit outcome tag,
    HTTP method, path, status code, duration, and response msg.

    Log level adapts to the status code:
        2xx/3xx -> INFO    (SUCCESS)
        4xx     -> WARNING (CLIENT_ERROR)
        5xx     -> ERROR   (SERVER_ERROR)
    """

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        method = request.method
        path = request.url.path

        response = await call_next(request)

        body_bytes = b""
        async for chunk in response.body_iterator:
            body_bytes += chunk if isinstance(chunk, bytes) else chunk.encode()

        msg = ""
        if body_bytes:
            try:
                data = json.loads(body_bytes)
                if isinstance(data, dict):
                    msg = str(data.get("msg", "") or "")
            except (ValueError, UnicodeDecodeError):
                msg = ""

        if not msg:
            try:
                msg = http.HTTPStatus(response.status_code).phrase
            except ValueError:
                msg = ""

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        status_code = response.status_code

        if 200 <= status_code < 400:
            tag = "SUCCESS"
            log_fn = logger.info
        elif 400 <= status_code < 500:
            tag = "CLIENT_ERROR"
            log_fn = logger.warning
        else:
            tag = "SERVER_ERROR"
            log_fn = logger.error

        log_fn(
            f"RESPONSE {tag} {method} {path} "
            f"status={status_code} duration={duration_ms}ms msg={msg}"
        )

        excluded_headers = {"content-length", "content-encoding"}
        passthrough_headers = {
            k: v for k, v in response.headers.items() if k.lower() not in excluded_headers
        }

        return Response(
            content=body_bytes,
            status_code=status_code,
            headers=passthrough_headers,
            media_type=response.media_type,
        )

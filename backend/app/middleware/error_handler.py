"""Error handling middleware.

Returns generic error messages to clients while logging
full stack traces server-side. Prevents information leakage.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catches unhandled exceptions and returns safe error responses.

    Full stack traces are logged server-side only — clients receive
    generic messages to prevent information leakage.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and handle any unhandled exceptions."""
        try:
            response = await call_next(request)
            return response
        except Exception:
            logger.exception(
                "Unhandled exception for %s %s",
                request.method,
                request.url.path,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal error occurred. Please try again later.",
                    "error_code": "INTERNAL_ERROR",
                },
            )

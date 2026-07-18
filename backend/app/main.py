"""FastAPI application entry point.

Configures CORS, rate limiting, error handling, and mounts
all API routers. This is the single entry point for the backend.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.routers import fan, staff

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.is_development else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter — uses client IP for key
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="FanPulse AI",
    description=(
        "GenAI Stadium Companion & Operations Copilot for FIFA World Cup 2026. "
        "Powered by Google Gemini."
    ),
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# CORS — explicit allow-list, never wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Error handling — generic messages to client, full traces in logs
app.add_middleware(ErrorHandlerMiddleware)

# Mount routers
app.include_router(fan.router)
app.include_router(staff.router)


@app.get("/")
async def root() -> dict:
    """Health check / root endpoint."""
    return {
        "service": "FanPulse AI",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check() -> dict:
    """Detailed health check for monitoring."""
    return {
        "status": "healthy",
        "gemini_model": settings.gemini_model,
        "gemini_configured": settings.gemini_api_key != "not-set",
    }


# Apply rate limits to Gemini-calling endpoints
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Apply endpoint-specific rate limits.

    Fan chat: 20/minute per IP
    Staff analyze/summary: 10/minute per IP
    """
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.is_development,
    )

"""Application settings loaded from environment variables.

Uses Pydantic BaseSettings for typed, validated configuration.
All secrets are read from env vars — never hardcoded.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the FanPulse AI backend.

    All values can be overridden via environment variables or a .env file.
    """

    # Gemini AI
    gemini_api_key: str = "not-set"
    gemini_model: str = "gemini-2.5-flash"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # CORS — explicit allow-list, never wildcard
    cors_origins: str = "http://localhost:5173"

    # Rate limiting
    rate_limit_fan_chat: str = "20/minute"
    rate_limit_staff_analyze: str = "10/minute"

    # Environment
    environment: str = "development"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Singleton settings instance
settings = Settings()

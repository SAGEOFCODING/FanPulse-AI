"""Shared test fixtures and configuration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_gemini_response():
    """Create a mock Gemini text generation response."""
    mock_response = MagicMock()
    mock_response.text = "This is a test response from the AI assistant."
    return mock_response


@pytest.fixture
def mock_gemini_client(mock_gemini_response):
    """Patch the Gemini client to return mock responses."""
    with patch("app.gemini.client.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_aio = MagicMock()

        # Mock async generate_content
        mock_models = MagicMock()
        mock_models.generate_content = AsyncMock(return_value=mock_gemini_response)
        mock_models.generate_content_stream = AsyncMock(return_value=iter([]))
        mock_aio.models = mock_models
        mock_client.aio = mock_aio

        mock_client_class.return_value = mock_client
        yield mock_client

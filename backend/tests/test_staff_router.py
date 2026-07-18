"""Integration tests for staff API endpoints with mocked Gemini."""

from unittest.mock import AsyncMock, MagicMock, patch


def test_get_crowd_data(client):
    """Crowd data endpoint returns simulated data."""
    response = client.get("/api/staff/crowd-data")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "gates" in data
    assert "weather" in data
    assert "summary" in data
    assert len(data["gates"]) == 8  # 8 gates A-H


def test_get_alerts(client):
    """Alerts endpoint returns structured alert data."""
    response = client.get("/api/staff/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert "total_count" in data
    assert "critical_count" in data
    assert "warning_count" in data


def test_alerts_have_required_fields(client):
    """Each alert has severity, gate_id, message, and timestamp."""
    response = client.get("/api/staff/alerts")
    data = response.json()
    for alert in data["alerts"]:
        assert "severity" in alert
        assert "gate_id" in alert
        assert "message" in alert
        assert "timestamp" in alert
        assert alert["severity"] in ("critical", "warning", "info")


def test_analyze_with_mocked_gemini(client):
    """Analyze endpoint returns AI analysis when Gemini is mocked."""
    mock_response = MagicMock()
    mock_response.text = "Gate D is approaching capacity. Recommend redirecting to Gate H."

    with patch("app.gemini.client.genai.Client") as mock_cls:
        mock_client = MagicMock()
        mock_aio = MagicMock()
        mock_models = MagicMock()
        mock_models.generate_content = AsyncMock(return_value=mock_response)
        mock_aio.models = mock_models
        mock_client.aio = mock_aio
        mock_cls.return_value = mock_client

        response = client.post(
            "/api/staff/analyze",
            json={"include_recommendations": True, "time_range_minutes": 30},
        )

    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "data_snapshot" in data


def test_summary_with_mocked_gemini(client):
    """Summary endpoint returns AI shift summary when Gemini is mocked."""
    mock_response = MagicMock()
    mock_response.text = "Shift summary: Operations ran smoothly with peak at 18:30."

    with patch("app.gemini.client.genai.Client") as mock_cls:
        mock_client = MagicMock()
        mock_aio = MagicMock()
        mock_models = MagicMock()
        mock_models.generate_content = AsyncMock(return_value=mock_response)
        mock_aio.models = mock_models
        mock_client.aio = mock_aio
        mock_cls.return_value = mock_client

        response = client.post(
            "/api/staff/summary",
            json={"shift_duration_minutes": 60},
        )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["shift_duration_minutes"] == 60
    assert data["data_points_analyzed"] > 0


def test_analyze_validates_time_range(client):
    """Analyze endpoint validates time_range_minutes bounds."""
    # Too short
    response = client.post(
        "/api/staff/analyze",
        json={"time_range_minutes": 2},
    )
    assert response.status_code == 422

    # Too long
    response = client.post(
        "/api/staff/analyze",
        json={"time_range_minutes": 500},
    )
    assert response.status_code == 422


def test_summary_validates_duration(client):
    """Summary endpoint validates shift_duration_minutes bounds."""
    response = client.post(
        "/api/staff/summary",
        json={"shift_duration_minutes": 5},  # Below minimum of 15
    )
    assert response.status_code == 422

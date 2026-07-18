"""Tests for the crowd density simulator."""

from app.data.simulator import (
    GATE_IDS,
    generate_current_signals,
    generate_gate_density,
    generate_time_series,
    generate_weather,
)


class TestGateDensity:
    """Tests for gate density generation."""

    def test_returns_all_gates(self):
        gates = generate_gate_density(minutes_before_kickoff=60)
        gate_ids = [g["gate_id"] for g in gates]
        assert set(gate_ids) == set(GATE_IDS)

    def test_density_in_valid_range(self):
        gates = generate_gate_density(minutes_before_kickoff=30)
        for gate in gates:
            assert 0 <= gate["density_percent"] <= 100

    def test_queue_length_non_negative(self):
        gates = generate_gate_density(minutes_before_kickoff=30)
        for gate in gates:
            assert gate["queue_length"] >= 0

    def test_status_matches_density(self):
        gates = generate_gate_density(minutes_before_kickoff=30)
        for gate in gates:
            if gate["density_percent"] > 85:
                assert gate["status"] == "critical"
            elif gate["density_percent"] > 70:
                assert gate["status"] == "warning"
            else:
                assert gate["status"] == "normal"

    def test_low_density_before_gates_open(self):
        """Density should be low when 3+ hours before kickoff."""
        gates = generate_gate_density(minutes_before_kickoff=180)
        avg = sum(g["density_percent"] for g in gates) / len(gates)
        assert avg < 30  # Should be low

    def test_deterministic_with_seed(self):
        """Same seed should produce same results."""
        gates1 = generate_gate_density(minutes_before_kickoff=60)
        gates2 = generate_gate_density(minutes_before_kickoff=60)
        assert gates1 == gates2


class TestWeather:
    """Tests for weather generation."""

    def test_weather_has_required_fields(self):
        weather = generate_weather()
        assert "condition" in weather
        assert "temperature_celsius" in weather
        assert "humidity_percent" in weather
        assert "wind_speed_kmh" in weather

    def test_temperature_in_reasonable_range(self):
        weather = generate_weather()
        assert -10 <= weather["temperature_celsius"] <= 50

    def test_humidity_in_valid_range(self):
        weather = generate_weather()
        assert 0 <= weather["humidity_percent"] <= 100


class TestCurrentSignals:
    """Tests for the main signal generator."""

    def test_has_required_keys(self):
        signals = generate_current_signals()
        assert "timestamp" in signals
        assert "gates" in signals
        assert "weather" in signals
        assert "summary" in signals
        assert signals["_simulated"] is True

    def test_summary_has_stats(self):
        signals = generate_current_signals()
        summary = signals["summary"]
        assert "average_density_percent" in summary
        assert "busiest_gate" in summary
        assert "quietest_gate" in summary
        assert "total_estimated_fans" in summary

    def test_gates_count(self):
        signals = generate_current_signals()
        assert len(signals["gates"]) == len(GATE_IDS)


class TestTimeSeries:
    """Tests for historical time series generation."""

    def test_correct_number_of_points(self):
        series = generate_time_series(duration_minutes=60, interval_minutes=5)
        assert len(series) == 12  # 60/5

    def test_points_have_required_fields(self):
        series = generate_time_series(duration_minutes=30, interval_minutes=10)
        for point in series:
            assert "timestamp" in point
            assert "gates" in point
            assert "average_density" in point

    def test_chronological_order(self):
        series = generate_time_series(duration_minutes=30, interval_minutes=5)
        timestamps = [p["timestamp"] for p in series]
        assert timestamps == sorted(timestamps)

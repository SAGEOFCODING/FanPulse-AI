"""Deterministic crowd density and operational signal simulator.

Generates synthetic real-time data for the staff command center.
Uses seeded random for reproducible results — all data is clearly
simulated, not sourced from real IoT sensors.

NOTE: This is simulated data for demonstration purposes only.
No real stadium sensor data is used or collected.
"""

import math
import random
from datetime import datetime, timedelta

# Gate IDs matching zones.json
GATE_IDS = ["A", "B", "C", "D", "E", "F", "G", "H"]

# Weather conditions for simulation variety
WEATHER_CONDITIONS = ["Clear", "Partly Cloudy", "Overcast", "Light Rain", "Hot & Humid"]

# Seed for reproducibility
_SIMULATOR_SEED = 42


def _get_seeded_random(seed_offset: int = 0) -> random.Random:
    """Return a seeded Random instance for deterministic output."""
    rng = random.Random(_SIMULATOR_SEED + seed_offset)  # noqa: S311
    return rng


def generate_gate_density(
    minutes_before_kickoff: int,
    rng: random.Random | None = None,
) -> list[dict]:
    """Generate crowd density data for each gate.

    Density follows a realistic pattern:
    - Low density 3+ hours before kickoff
    - Gradual increase starting 2 hours before
    - Peak 30-60 minutes before kickoff
    - Decrease after kickoff as fans are seated

    Args:
        minutes_before_kickoff: Minutes remaining until match start.
            Positive = before kickoff, negative = after kickoff.
        rng: Optional seeded Random instance.

    Returns:
        List of gate density records with capacity percentages.
    """
    if rng is None:
        rng = _get_seeded_random()

    gates = []
    for gate_id in GATE_IDS:
        # Base density curve — sigmoid-like approach to peak
        if minutes_before_kickoff > 120:
            base = 15.0  # Low early arrival
        elif minutes_before_kickoff > 60:
            # Ramping up
            progress = (120 - minutes_before_kickoff) / 60.0
            base = 15.0 + 50.0 * progress
        elif minutes_before_kickoff > 0:
            # Peak period
            progress = (60 - minutes_before_kickoff) / 60.0
            base = 65.0 + 25.0 * math.sin(progress * math.pi / 2)
        else:
            # After kickoff — clearing
            minutes_after = abs(minutes_before_kickoff)
            base = max(10.0, 90.0 - minutes_after * 2.0)

        # Per-gate variation (some gates are consistently busier)
        gate_bias = {
            "A": 1.15,  # Main entrance, always busy
            "B": 1.05,
            "C": 0.95,
            "D": 0.90,
            "E": 1.10,  # Near parking
            "F": 0.85,
            "G": 0.95,
            "H": 0.80,  # Least popular
        }

        density = base * gate_bias.get(gate_id, 1.0)
        # Add controlled noise
        noise = rng.gauss(0, 3.0)
        density = max(0, min(100, density + noise))

        # Queue length correlates with density
        queue_length = max(0, int(density * 0.8 + rng.randint(-5, 15)))

        gates.append(
            {
                "gate_id": gate_id,
                "density_percent": round(density, 1),
                "queue_length": queue_length,
                "estimated_wait_minutes": max(0, round(queue_length * 0.3, 1)),
                "status": (
                    "critical" if density > 85 else "warning" if density > 70 else "normal"
                ),
            }
        )

    return gates


def generate_weather() -> dict:
    """Generate current simulated weather conditions."""
    rng = _get_seeded_random(seed_offset=100)
    condition = rng.choice(WEATHER_CONDITIONS)

    temp_ranges = {
        "Clear": (28, 35),
        "Partly Cloudy": (25, 32),
        "Overcast": (22, 28),
        "Light Rain": (18, 25),
        "Hot & Humid": (33, 40),
    }
    temp_min, temp_max = temp_ranges[condition]
    temperature = rng.randint(temp_min, temp_max)

    return {
        "condition": condition,
        "temperature_celsius": temperature,
        "humidity_percent": rng.randint(40, 85),
        "wind_speed_kmh": rng.randint(5, 25),
        "uv_index": rng.randint(3, 10) if condition != "Light Rain" else rng.randint(1, 4),
        "heat_advisory": temperature > 35,
    }


def generate_current_signals() -> dict:
    """Generate a complete snapshot of current operational signals.

    Returns a dict containing gate densities, weather, and aggregate stats.
    This is the primary data source for the staff command center.
    """
    # Use current time to derive a realistic "minutes before kickoff" value
    # Simulate a match starting at 19:00 local time
    now = datetime.now()
    kickoff = now.replace(hour=19, minute=0, second=0, microsecond=0)
    if now > kickoff:
        # If past 7pm, simulate next day's match
        kickoff += timedelta(days=1)
    minutes_before = int((kickoff - now).total_seconds() / 60)

    # Cap to reasonable range for demo
    minutes_before = max(-30, min(180, minutes_before))

    rng = _get_seeded_random(seed_offset=int(now.timestamp()) % 1000)
    gate_data = generate_gate_density(minutes_before, rng)
    weather = generate_weather()

    # Aggregate statistics
    densities = [g["density_percent"] for g in gate_data]
    avg_density = round(sum(densities) / len(densities), 1)
    max_gate = max(gate_data, key=lambda g: g["density_percent"])
    min_gate = min(gate_data, key=lambda g: g["density_percent"])

    critical_gates = [g["gate_id"] for g in gate_data if g["status"] == "critical"]
    warning_gates = [g["gate_id"] for g in gate_data if g["status"] == "warning"]

    return {
        "timestamp": now.isoformat(),
        "minutes_before_kickoff": minutes_before,
        "gates": gate_data,
        "weather": weather,
        "summary": {
            "average_density_percent": avg_density,
            "busiest_gate": max_gate["gate_id"],
            "busiest_gate_density": max_gate["density_percent"],
            "quietest_gate": min_gate["gate_id"],
            "quietest_gate_density": min_gate["density_percent"],
            "critical_gates": critical_gates,
            "warning_gates": warning_gates,
            "total_estimated_fans": int(avg_density * 82500 / 100),
        },
        "_simulated": True,
        "_note": "All data is synthetically generated for demonstration purposes",
    }


def generate_time_series(duration_minutes: int = 60, interval_minutes: int = 5) -> list[dict]:
    """Generate a historical time series of crowd signals.

    Useful for the shift summary report — shows how conditions
    evolved over a time period.

    Args:
        duration_minutes: How many minutes of history to generate.
        interval_minutes: Time between data points.

    Returns:
        List of signal snapshots ordered chronologically.
    """
    series = []
    now = datetime.now()

    for i in range(0, duration_minutes, interval_minutes):
        timestamp = now - timedelta(minutes=duration_minutes - i)
        minutes_before = 90 - i  # Simulate the pre-kickoff ramp-up

        rng = _get_seeded_random(seed_offset=i * 7)
        gate_data = generate_gate_density(minutes_before, rng)

        densities = [g["density_percent"] for g in gate_data]
        avg_density = round(sum(densities) / len(densities), 1)

        series.append(
            {
                "timestamp": timestamp.isoformat(),
                "minutes_before_kickoff": minutes_before,
                "gates": gate_data,
                "average_density": avg_density,
            }
        )

    return series

"""Staff/Operations API endpoints.

Provides crowd data, AI-powered analysis, alerts, and shift
summary generation for the staff command center view.
"""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Request

from app.data.simulator import generate_current_signals, generate_time_series
from app.gemini.client import generate_text
from app.gemini.prompts import (
    build_staff_analysis_prompt,
    get_shift_summary_prompt,
    get_staff_ops_system_prompt,
)
from app.models.staff import (
    AnalysisResponse,
    AnalyzeRequest,
    CrowdDataResponse,
    SummaryRequest,
    SummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/staff", tags=["staff"])


@router.get("/crowd-data")
async def get_crowd_data(request: Request) -> CrowdDataResponse:
    """Return current simulated crowd density data.

    Data is generated fresh on each call to simulate real-time
    sensor updates. All data is synthetic — see simulator.py.
    """
    signals = generate_current_signals()
    return CrowdDataResponse(
        timestamp=signals["timestamp"],
        minutes_before_kickoff=signals["minutes_before_kickoff"],
        gates=signals["gates"],
        weather=signals["weather"],
        summary=signals["summary"],
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_crowd(request: Request, body: AnalyzeRequest) -> AnalysisResponse:
    """AI-powered analysis of current crowd conditions.

    Gemini analyzes the simulated crowd signals and generates
    actionable operational recommendations with severity-tagged alerts.
    """
    # Get current signals for analysis
    signals = generate_current_signals()
    signals_json = json.dumps(signals, indent=2, default=str)

    system_prompt = get_staff_ops_system_prompt()
    analysis_prompt = build_staff_analysis_prompt(signals_json)

    analysis_text = await generate_text(
        prompt=analysis_prompt,
        system_instruction=system_prompt,
        temperature=0.4,  # Lower temperature for more focused analysis
    )

    return AnalysisResponse(
        analysis=analysis_text,
        data_snapshot=signals,
    )


@router.post("/summary", response_model=SummaryResponse)
async def generate_shift_summary(request: Request, body: SummaryRequest) -> SummaryResponse:
    """Generate an AI-written end-of-shift summary report.

    Analyzes a time series of crowd signals from the shift period
    and produces a comprehensive report for handoff.
    """
    # Generate historical time series for the shift
    time_series = generate_time_series(
        duration_minutes=body.shift_duration_minutes,
        interval_minutes=5,
    )
    series_json = json.dumps(time_series, indent=2, default=str)

    system_prompt = get_staff_ops_system_prompt()
    summary_prompt = get_shift_summary_prompt(series_json)

    summary_text = await generate_text(
        prompt=summary_prompt,
        system_instruction=system_prompt,
        temperature=0.5,
    )

    return SummaryResponse(
        summary=summary_text,
        shift_duration_minutes=body.shift_duration_minutes,
        data_points_analyzed=len(time_series),
    )


@router.get("/alerts")
async def get_alerts(request: Request) -> dict:
    """Return current alerts based on crowd density thresholds.

    Generates rule-based alerts (not AI) for immediate display,
    plus an AI-generated analysis if conditions warrant.
    """
    signals = generate_current_signals()
    alerts = []

    for gate in signals["gates"]:
        if gate["status"] == "critical":
            alerts.append(
                {
                    "severity": "critical",
                    "gate_id": gate["gate_id"],
                    "message": (
                        f"Gate {gate['gate_id']} at {gate['density_percent']}% capacity — "
                        f"queue length: {gate['queue_length']} people, "
                        f"est. wait: {gate['estimated_wait_minutes']} min. "
                        f"Consider redirecting fans to nearby gates."
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            )
        elif gate["status"] == "warning":
            alerts.append(
                {
                    "severity": "warning",
                    "gate_id": gate["gate_id"],
                    "message": (
                        f"Gate {gate['gate_id']} approaching capacity at "
                        f"{gate['density_percent']}% — monitor closely."
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            )

    # Weather-based alerts
    weather = signals["weather"]
    if weather.get("heat_advisory"):
        alerts.append(
            {
                "severity": "warning",
                "gate_id": "ALL",
                "message": (
                    f"Heat advisory: {weather['temperature_celsius']}°C. "
                    f"Ensure water stations are stocked and medical teams are on standby."
                ),
                "timestamp": datetime.now().isoformat(),
            }
        )

    return {
        "alerts": alerts,
        "total_count": len(alerts),
        "critical_count": sum(1 for a in alerts if a["severity"] == "critical"),
        "warning_count": sum(1 for a in alerts if a["severity"] == "warning"),
        "data_timestamp": signals["timestamp"],
    }

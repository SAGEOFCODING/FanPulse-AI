"""Pydantic models for staff/operations API endpoints.

Validates input for operational intelligence features.
"""

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request for AI-powered crowd analysis."""

    include_recommendations: bool = Field(
        default=True,
        description="Whether to include actionable recommendations",
    )
    time_range_minutes: int = Field(
        default=30,
        description="Minutes of historical data to analyze",
        ge=5,
        le=120,
    )


class SummaryRequest(BaseModel):
    """Request for an AI-generated shift summary report."""

    shift_duration_minutes: int = Field(
        default=60,
        description="Duration of the shift to summarize",
        ge=15,
        le=480,
    )


class AlertItem(BaseModel):
    """A single operational alert."""

    severity: str = Field(
        ...,
        description="Alert severity level",
        pattern="^(critical|warning|info)$",
    )
    gate_id: str = Field(..., description="Affected gate ID")
    message: str = Field(..., description="Alert description")
    timestamp: str = Field(..., description="ISO timestamp")


class CrowdDataResponse(BaseModel):
    """Response containing current crowd density data."""

    timestamp: str
    minutes_before_kickoff: int
    gates: list[dict]
    weather: dict
    summary: dict


class AnalysisResponse(BaseModel):
    """AI-generated operational analysis."""

    analysis: str = Field(..., description="Gemini-generated analysis text")
    data_snapshot: dict = Field(..., description="The data that was analyzed")


class SummaryResponse(BaseModel):
    """AI-generated shift summary report."""

    summary: str = Field(..., description="Gemini-generated summary report")
    shift_duration_minutes: int
    data_points_analyzed: int

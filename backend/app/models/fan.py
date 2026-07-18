"""Pydantic models for fan-facing API endpoints.

All user input is validated and typed through these models
before being processed or sent to Gemini.
"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in the conversation history."""

    role: str = Field(
        ...,
        description="Message sender role",
        pattern="^(user|assistant)$",
    )
    content: str = Field(
        ...,
        description="Message text content",
        min_length=1,
        max_length=5000,
    )


class ChatRequest(BaseModel):
    """Fan chat request — validated before any Gemini interaction."""

    message: str = Field(
        ...,
        description="The fan's current message",
        min_length=1,
        max_length=2000,
    )
    conversation_history: list[ChatMessage] = Field(
        default_factory=list,
        description="Previous messages for context",
        max_length=50,
    )
    accessibility_mode: bool = Field(
        default=False,
        description="Enable simplified language and clearer directions",
    )


class ChatResponse(BaseModel):
    """Non-streaming chat response."""

    response: str = Field(..., description="AI-generated response text")
    cached: bool = Field(default=False, description="Whether response was served from cache")


class FacilityItem(BaseModel):
    """A single facility or point of interest."""

    id: str
    name: str
    location: str
    description: str = ""
    nearest_gate: str = ""
    type: str = ""


class TransportRoute(BaseModel):
    """A transport route or service."""

    id: str
    name: str
    route: str = ""
    frequency_minutes: int = 0
    nearest_gate: str = ""
    accessible: bool = True

"""Fan-facing API endpoints.

Provides the AI concierge chat interface and stadium data lookups
for the fan view. All endpoints validate input via Pydantic models.
"""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import typing

from app.limiter import limiter
from app.gemini.cache import prompt_cache
from app.gemini.client import generate_text, generate_text_stream
from app.gemini.prompts import build_fan_prompt, get_fan_concierge_system_prompt
from app.models.fan import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/fan", tags=["fan"])

# Lazy-load fixture data
_fixtures_dir = Path(__file__).parent.parent / "data" / "fixtures"


def _load_json(filename: str) -> dict[str, typing.Any]:
    """Load a JSON fixture file."""
    filepath = _fixtures_dir / filename
    with open(filepath, encoding="utf-8") as f:
        return typing.cast(dict[str, typing.Any], json.load(f))


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def fan_chat(request: Request, body: ChatRequest) -> ChatResponse:
    """AI concierge chat endpoint (non-streaming fallback).

    For clients that don't support SSE streaming. Checks cache first
    for FAQ-style repeated questions to reduce API cost.
    """
    # Check cache for simple, no-history queries (likely FAQs)
    if not body.conversation_history:
        cached = prompt_cache.get(body.message)
        if cached:
            return ChatResponse(response=cached, cached=True)

    system_prompt = get_fan_concierge_system_prompt()
    user_prompt = build_fan_prompt(body.message, body.accessibility_mode)

    response_text = await generate_text(
        prompt=user_prompt,
        system_instruction=system_prompt,
    )

    # Cache simple queries (no conversation history)
    if not body.conversation_history:
        prompt_cache.put(body.message, response_text)

    return ChatResponse(response=response_text, cached=False)


@router.post("/chat/stream")
@limiter.limit("20/minute")
async def fan_chat_stream(request: Request, body: ChatRequest) -> StreamingResponse:
    """Streaming AI concierge chat via Server-Sent Events.

    Streams Gemini responses token-by-token for a responsive
    chat experience. Falls back to a complete response if
    streaming fails.
    """
    system_prompt = get_fan_concierge_system_prompt()
    user_prompt = build_fan_prompt(body.message, body.accessibility_mode)

    # Convert conversation history to the format expected by Gemini
    history = [{"role": msg.role, "content": msg.content} for msg in body.conversation_history]

    stream = await generate_text_stream(
        prompt=user_prompt,
        system_instruction=system_prompt,
        conversation_history=history,
    )

    async def event_generator() -> typing.AsyncGenerator[str, None]:
        """Yield SSE-formatted chunks from Gemini stream."""
        if stream is None:
            yield (
                "data: I'm experiencing a temporary issue. " "Please try again in a moment.\n\n"
            )
            yield "data: [DONE]\n\n"
            return

        try:
            async for chunk in stream:
                if chunk.text:
                    # Escape newlines for SSE format
                    text = chunk.text.replace("\n", "\\n")
                    yield f"data: {text}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.exception("Error during Gemini streaming")
            yield f"data: I encountered an issue. Details: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/facilities")
async def get_facilities() -> dict:
    """Return stadium facilities data (accessibility, sustainability, etc.)."""
    data = _load_json("facilities.json")
    return data


@router.get("/transport")
async def get_transport() -> dict:
    """Return transportation schedules and options."""
    data = _load_json("transport.json")
    return data


@router.get("/zones")
async def get_zones() -> dict:
    """Return stadium zones and gate information."""
    data = _load_json("zones.json")
    return data


@router.get("/faq")
async def get_faq() -> dict:
    """Return frequently asked questions."""
    data = _load_json("faq.json")
    return data

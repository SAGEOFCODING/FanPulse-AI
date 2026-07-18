"""Gemini AI client singleton with safety settings and error handling.

Provides a configured genai.Client instance with appropriate safety
settings for a public-facing stadium assistant application.
"""

import logging
from typing import Any

from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)

# Safety settings — block medium and above for all harm categories
# to ensure family-friendly stadium assistant responses.
SAFETY_SETTINGS: list[types.SafetySetting] = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
]


def get_gemini_client() -> genai.Client:
    """Return a configured Gemini client instance.

    The client is created fresh each call (lightweight) to avoid
    stale connection issues in long-running servers.
    """
    if settings.gemini_api_key == "not-set":
        logger.warning("GEMINI_API_KEY is not set — AI features will fail")

    return genai.Client(api_key=settings.gemini_api_key)


async def generate_text(
    prompt: str,
    system_instruction: str | None = None,
    temperature: float = 0.7,
) -> str:
    """Generate text from Gemini with safety settings and error handling.

    Args:
        prompt: The user-facing prompt content.
        system_instruction: Optional system-level instruction for the model.
        temperature: Creativity control (0.0 = deterministic, 1.0 = creative).

    Returns:
        Generated text string, or a fallback error message if generation fails.
    """
    client = get_gemini_client()

    config = types.GenerateContentConfig(
        temperature=temperature,
        safety_settings=SAFETY_SETTINGS,
    )
    if system_instruction:
        config.system_instruction = system_instruction

    try:
        response = await client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=config,
        )

        # Handle blocked or empty responses gracefully
        if not response.text:
            logger.warning("Gemini returned empty response for prompt: %s", prompt[:100])
            return (
                "I apologize, but I'm unable to provide a response to that query. "
                "Please try rephrasing your question."
            )

        return response.text

    except Exception:
        logger.exception("Gemini API call failed")
        return (
            "I'm experiencing a temporary issue connecting to the AI service. "
            "Please try again in a moment."
        )


async def generate_text_stream(
    prompt: str,
    system_instruction: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    temperature: float = 0.7,
) -> Any:
    """Stream text from Gemini for real-time chat responses.

    Args:
        prompt: The latest user message.
        system_instruction: Optional system-level instruction.
        conversation_history: Previous messages for context.
        temperature: Creativity control.

    Yields:
        Async iterator of text chunks from Gemini.
    """
    client = get_gemini_client()

    config = types.GenerateContentConfig(
        temperature=temperature,
        safety_settings=SAFETY_SETTINGS,
    )
    if system_instruction:
        config.system_instruction = system_instruction

    # Build contents list from conversation history + current message
    contents: list[types.Content] = []
    if conversation_history:
        for msg in conversation_history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

    contents.append(types.Content(role="user", parts=[types.Part(text=prompt)]))

    try:
        stream = await client.aio.models.generate_content_stream(
            model=settings.gemini_model,
            contents=contents,
            config=config,
        )
        return stream

    except Exception:
        logger.exception("Gemini streaming API call failed")
        return None

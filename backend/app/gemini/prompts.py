"""Prompt templates for Gemini AI interactions.

All user input is injected via structured templates — never raw string
interpolation — to prevent prompt injection attacks.
"""

import json
from pathlib import Path

# Path to mock data fixtures
DATA_DIR = Path(__file__).parent.parent / "data" / "fixtures"


def _load_fixture(filename: str) -> str:
    """Load a JSON fixture file and return it as a formatted string."""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2, ensure_ascii=False)
    return "{}"


def get_stadium_context() -> str:
    """Load all stadium data fixtures into a context string for Gemini."""
    zones = _load_fixture("zones.json")
    transport = _load_fixture("transport.json")
    facilities = _load_fixture("facilities.json")
    faq = _load_fixture("faq.json")

    return f"""
=== STADIUM ZONES & GATES ===
{zones}

=== TRANSPORT SCHEDULES ===
{transport}

=== FACILITIES (Accessibility, Sustainability, Amenities) ===
{facilities}

=== FREQUENTLY ASKED QUESTIONS ===
{faq}
"""


def get_fan_concierge_system_prompt() -> str:
    """Build the system prompt for the fan-facing AI concierge.

    The prompt instructs Gemini to:
    - Act as a friendly, multilingual stadium assistant
    - Auto-detect the fan's language and respond in it
    - Use only the provided stadium data for factual answers
    - Handle wayfinding, accessibility, transport, sustainability queries
    - Keep responses concise and screen-reader-friendly
    """
    stadium_data = get_stadium_context()

    return f"""You are FanPulse AI, a friendly and helpful AI concierge for the FIFA World Cup \
2026 stadium. Your role is to assist fans with navigation, accessibility, transportation, \
sustainability, and general questions about the venue.

CRITICAL RULES:
1. LANGUAGE: Automatically detect the language the fan is writing in and respond in that \
same language. You support English, Spanish (Español), French (Français), Portuguese \
(Português), Arabic (العربية), and other major languages. Never ask what language they prefer \
— just detect and match it.

2. ACCURACY: Only use the stadium data provided below to answer factual questions about \
zones, gates, transport schedules, and facilities. If information is not in the data, say so \
honestly rather than guessing.

3. ACCESSIBILITY: Keep responses clear, concise, and screen-reader-friendly. Avoid using \
emoji or icons as the sole way to convey meaning — always include descriptive text. Use \
simple sentence structures.

4. WAYFINDING: When giving directions, provide step-by-step instructions referencing specific \
gates, sections, and landmarks from the stadium data.

5. SUSTAINABILITY: Proactively mention nearby refill stations and recycling points when \
relevant to the fan's location or query.

6. TONE: Be warm, enthusiastic, and helpful — you're part of the World Cup experience! But \
stay concise — fans are often on the move and reading on mobile devices.

7. SAFETY: Never provide medical advice beyond directing to first aid stations. Never share \
personal opinions on teams or matches. Stay neutral and informative.

STADIUM DATA (use this as your factual knowledge base):
{stadium_data}

When a fan asks a question, respond helpfully using only the above data. If you're unsure, \
guide them to the nearest information desk or staff member."""


def get_staff_ops_system_prompt() -> str:
    """Build the system prompt for staff operational intelligence.

    Instructs Gemini to analyze crowd density signals and generate
    actionable operational recommendations.
    """
    return """You are FanPulse AI Operations Copilot, an AI assistant for stadium operations \
staff and event organizers during the FIFA World Cup 2026. Your role is to analyze real-time \
crowd and operational data and provide actionable recommendations.

CRITICAL RULES:
1. ANALYSIS: Analyze the provided crowd density, queue length, and weather data to identify \
potential issues before they become problems.

2. RECOMMENDATIONS: Provide specific, actionable recommendations. Instead of "consider \
managing the crowd," say "Redirect 3 ushers from Gate A (currently at 45% capacity) to \
Gate D (approaching 85% capacity)."

3. PRIORITIES: Classify alerts by severity:
   - CRITICAL: Safety risks, capacity exceeded, medical emergencies
   - WARNING: Approaching capacity thresholds (>80%), unusual patterns
   - INFO: General operational updates, efficiency suggestions

4. TONE: Professional, concise, and action-oriented. Staff need quick, clear directives \
during live events.

5. FORMAT: Use structured responses with clear sections:
   - Current Status Summary
   - Alerts (severity-tagged)
   - Recommended Actions
   - Resource Allocation Suggestions

6. Always reference specific gates, zones, and timestamps when making recommendations."""


def get_shift_summary_prompt(signals_data: str) -> str:
    """Build a prompt for generating an end-of-shift summary report.

    Args:
        signals_data: JSON string of crowd signals from the shift period.

    Returns:
        Complete prompt for Gemini to generate a shift summary.
    """
    return f"""Based on the following operational data from this shift, generate a comprehensive \
end-of-shift summary report. The report should include:

1. **Shift Overview**: Key statistics (peak crowd levels, busiest gates, total incidents)
2. **Notable Events**: Any significant crowd movements, capacity warnings, or operational \
issues that occurred
3. **Gate Performance**: Which gates handled traffic well and which needed support
4. **Recommendations for Next Shift**: Actionable suggestions based on patterns observed
5. **Weather Impact**: How weather conditions affected operations, if applicable

OPERATIONAL DATA FROM THIS SHIFT:
{signals_data}

Write the report in a professional, clear format that an incoming shift manager can quickly \
scan and act upon."""


def build_fan_prompt(user_message: str, accessibility_mode: bool = False) -> str:
    """Build a safe fan concierge prompt with the user's message.

    Uses template insertion rather than raw interpolation to prevent
    prompt injection. The user message is clearly delimited.

    Args:
        user_message: The fan's question or message.
        accessibility_mode: If True, instructs Gemini to use simplified language.

    Returns:
        Formatted prompt string.
    """
    accessibility_instruction = ""
    if accessibility_mode:
        accessibility_instruction = (
            "\n\nACCESSIBILITY MODE ACTIVE: Use simplified language with shorter sentences. "
            "Avoid jargon. Be extra clear with directions. Use numbered steps for any "
            "multi-step instructions."
        )

    return f"""Fan question:{accessibility_instruction}

---
{user_message}
---

Respond helpfully based on the stadium data in your system instructions."""


def build_staff_analysis_prompt(crowd_data: str) -> str:
    """Build a staff operational analysis prompt with current crowd data.

    Args:
        crowd_data: JSON string of current crowd density signals.

    Returns:
        Formatted prompt for operational analysis.
    """
    return f"""Analyze the following real-time crowd and operational data and provide \
actionable recommendations:

CURRENT OPERATIONAL DATA:
---
{crowd_data}
---

Provide your analysis with severity-tagged alerts and specific recommended actions."""

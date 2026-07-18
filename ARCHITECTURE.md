# FanPulse AI — Architecture

> GenAI Stadium Companion & Operations Copilot for FIFA World Cup 2026

## System Overview

FanPulse AI is a single-platform stadium companion with two front-ends sharing one Gemini-based backend. The architecture is deliberately lightweight to keep the repo under 10 MB, fast to build, and simple to deploy.

## Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                        React + Vite Frontend                      │
│                                                                    │
│  ┌─────────────────────┐     ┌──────────────────────────┐        │
│  │    Fan View          │     │    Staff View             │        │
│  │  (/fan)              │     │  (/staff)                 │        │
│  │                      │     │                           │        │
│  │  • Chat UI (SSE)     │     │  • Crowd Heatmap (SVG)    │        │
│  │  • Quick Actions     │     │  • Alerts Feed            │        │
│  │  • A11y Toggle       │     │  • AI Analysis            │        │
│  │                      │     │  • Shift Summary          │        │
│  └──────────┬───────────┘     └─────────┬────────────────┘        │
│             │                           │                          │
│             ▼                           ▼                          │
│  ┌──────────────────────────────────────────────────────┐         │
│  │              API Service Layer (fetch)                │         │
│  │         /api/fan/*        /api/staff/*                │         │
│  └──────────────────────────────────────────────────────┘         │
└──────────────────────────────┬────────────────────────────────────┘
                               │ HTTP (Vite dev proxy)
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Python)                       │
│                                                                    │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐   │
│  │  Fan Router      │  │  Staff Router     │  │  Error Handler │   │
│  │  /api/fan/*      │  │  /api/staff/*     │  │  Middleware     │   │
│  └────────┬─────────┘  └────────┬──────────┘  └────────────────┘   │
│           │                     │                                   │
│           ▼                     ▼                                   │
│  ┌──────────────────────────────────────────────────────┐         │
│  │              Gemini Service Layer                     │         │
│  │                                                       │         │
│  │  • client.py  — Async Gemini client + safety settings │         │
│  │  • prompts.py — System prompts + template builder     │         │
│  │  • cache.py   — LRU cache for FAQ responses           │         │
│  └──────────────────────┬───────────────────────────────┘         │
│                         │                                          │
│           ┌─────────────┼──────────────┐                           │
│           ▼             ▼              ▼                           │
│  ┌──────────────┐ ┌──────────┐ ┌──────────────────┐              │
│  │ Mock Data    │ │ Simulator│ │ Gemini API       │              │
│  │ (JSON)       │ │ (Python) │ │ (google-genai)   │              │
│  │ zones.json   │ │ crowd    │ │ gemini-2.5-flash │              │
│  │ transport    │ │ density  │ │                   │              │
│  │ facilities   │ │ weather  │ │ Safety settings   │              │
│  │ faq          │ │ alerts   │ │ Streaming support │              │
│  └──────────────┘ └──────────┘ └──────────────────┘              │
│                                                                    │
│  Cross-cutting: CORS (explicit), Rate Limiting (slowapi),          │
│                 Pydantic validation, Generic error responses        │
└──────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### Fan Chat Flow (Streaming)

1. Fan types a message in the ChatInput component
2. `useChat` hook sends POST to `/api/fan/chat/stream`
3. Fan Router receives the request, validates via Pydantic
4. Checks LRU cache for FAQ-style matches (simple queries without history)
5. Builds prompt: system instruction (with stadium data) + user message (delimited)
6. Calls `client.aio.models.generate_content_stream()` with safety settings
7. Streams chunks back as Server-Sent Events (SSE)
8. Frontend receives chunks and updates the ChatMessage in real-time
9. On completion, response is optionally cached for future FAQ matches

### Staff Analysis Flow

1. Staff clicks "AI Analysis" button on Command Center
2. `StaffView` calls POST `/api/staff/analyze`
3. Staff Router generates current crowd signals via `simulator.py`
4. Builds analysis prompt with the crowd data JSON
5. Calls Gemini with lower temperature (0.4) for focused analysis
6. Returns severity-tagged recommendations
7. Frontend displays in the Analysis panel

### Crowd Data Auto-Refresh

1. `StaffView` sets up 10-second interval on mount
2. Each tick calls GET `/api/staff/crowd-data` and GET `/api/staff/alerts`
3. Backend generates fresh simulated data on each call
4. Frontend updates heatmap colors and alerts feed
5. Interval cleared on component unmount

## Security Architecture

- **API Key**: Stored server-side only in environment variable, never exposed to frontend
- **Input Validation**: All requests validated by Pydantic models before processing
- **Prompt Safety**: User input injected via delimited templates, never raw interpolation
- **Rate Limiting**: Per-IP limits via slowapi (20/min fan chat, 10/min staff analysis)
- **CORS**: Explicit origin allow-list, not wildcard
- **Error Handling**: Generic messages to client, full stack traces in server logs only
- **Gemini Safety**: Content filtering enabled (BLOCK_MEDIUM_AND_ABOVE for all categories)

## Mock Data Layer

All "real-time" data is synthetically generated for demonstration:

- **Stadium Data**: Hand-written JSON fixtures (~5 KB each)
  - `zones.json` — 8 zones, 8 gates, coordinates, landmarks
  - `transport.json` — shuttle routes, metro, rideshare, parking
  - `facilities.json` — accessibility, sustainability, first aid, restrooms
  - `faq.json` — 15 common fan questions

- **Crowd Simulator** (`simulator.py`):
  - Seeded random for reproducibility
  - Realistic density curve (low → ramp → peak → clear)
  - Per-gate bias for variety
  - Weather condition generation
  - Time series generation for shift summaries

## Technology Decisions

| Decision | Rationale |
|---|---|
| React (not Next.js) | SPA is sufficient; no SSR needed; simpler build |
| Vanilla CSS (not Tailwind) | Full control, no build-time CSS processing, smaller footprint |
| SVG heatmap (not D3/Chart.js) | Zero extra dependency, small bundle, full design control |
| SSE (not WebSocket) | One-direction stream sufficient for chat; simpler to implement |
| In-memory cache (not Redis) | Single-process demo; no infra dependency |
| Seeded random (not real data) | Reproducible, no external dependencies, clearly simulated |

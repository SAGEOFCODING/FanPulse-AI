/**
 * API service layer for FanPulse AI frontend.
 *
 * All backend communication goes through these functions.
 * The Vite dev server proxies /api to the backend.
 */

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling.
 * @param {string} path - API path (e.g., '/fan/chat')
 * @param {object} options - Fetch options
 * @returns {Promise<object>} Parsed JSON response
 */
async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// ---- Fan Endpoints ---- //

/**
 * Send a chat message (non-streaming fallback).
 * @param {string} message - User message
 * @param {Array} conversationHistory - Previous messages
 * @param {boolean} accessibilityMode - Simplified language mode
 * @returns {Promise<object>} Chat response
 */
export async function sendChatMessage(
  message,
  conversationHistory = [],
  accessibilityMode = false,
) {
  return apiFetch('/fan/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory,
      accessibility_mode: accessibilityMode,
    }),
  });
}

/**
 * Send a chat message with SSE streaming.
 * @param {string} message - User message
 * @param {Array} conversationHistory - Previous messages
 * @param {boolean} accessibilityMode - Simplified language mode
 * @param {function} onChunk - Callback for each text chunk
 * @param {function} onDone - Callback when stream completes
 * @param {function} onError - Callback on error
 * @returns {function} Abort function to cancel the stream
 */
export function streamChatMessage(
  message,
  conversationHistory = [],
  accessibilityMode = false,
  onChunk,
  onDone,
  onError,
) {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/fan/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          conversation_history: conversationHistory,
          accessibility_mode: accessibilityMode,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Stream error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              onDone?.();
              return;
            }
            // Unescape newlines from SSE format
            const text = data.replace(/\\n/g, '\n');
            onChunk?.(text);
          }
        }
      }

      onDone?.();
    } catch (error) {
      if (error.name !== 'AbortError') {
        onError?.(error);
      }
    }
  })();

  return () => controller.abort();
}

/**
 * Get stadium facilities data.
 * @returns {Promise<object>} Facilities data
 */
export async function getFacilities() {
  return apiFetch('/fan/facilities');
}

/**
 * Get transport schedules.
 * @returns {Promise<object>} Transport data
 */
export async function getTransport() {
  return apiFetch('/fan/transport');
}

/**
 * Get stadium zones and gates.
 * @returns {Promise<object>} Zones data
 */
export async function getZones() {
  return apiFetch('/fan/zones');
}

// ---- Staff Endpoints ---- //

/**
 * Get current crowd density data.
 * @returns {Promise<object>} Crowd data
 */
export async function getCrowdData() {
  return apiFetch('/staff/crowd-data');
}

/**
 * Request AI-powered crowd analysis.
 * @param {number} timeRangeMinutes - Minutes of data to analyze
 * @returns {Promise<object>} Analysis results
 */
export async function analyzecrowd(timeRangeMinutes = 30) {
  return apiFetch('/staff/analyze', {
    method: 'POST',
    body: JSON.stringify({
      include_recommendations: true,
      time_range_minutes: timeRangeMinutes,
    }),
  });
}

/**
 * Generate AI shift summary report.
 * @param {number} shiftDurationMinutes - Shift duration to summarize
 * @returns {Promise<object>} Summary report
 */
export async function generateShiftSummary(shiftDurationMinutes = 60) {
  return apiFetch('/staff/summary', {
    method: 'POST',
    body: JSON.stringify({
      shift_duration_minutes: shiftDurationMinutes,
    }),
  });
}

/**
 * Get current operational alerts.
 * @returns {Promise<object>} Alerts data
 */
export async function getAlerts() {
  return apiFetch('/staff/alerts');
}

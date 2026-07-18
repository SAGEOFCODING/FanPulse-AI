/**
 * useChat hook — manages chat state, streaming, and conversation history.
 * Handles SSE streaming from the backend and maintains message history.
 */

import { useState, useCallback, useRef } from 'react';
import { streamChatMessage } from '../services/api';

/**
 * @param {boolean} accessibilityMode - Whether to request simplified language
 * @returns {object} Chat state and actions
 */
export function useChat(accessibilityMode = false) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  /**
   * Send a message and stream the response.
   * @param {string} userMessage - The message to send
   */
  const sendMessage = useCallback(
    (userMessage) => {
      if (!userMessage.trim() || isLoading) return;

      setError(null);

      // Add user message
      const newUserMsg = { role: 'user', content: userMessage.trim() };
      setMessages((prev) => [...prev, newUserMsg]);
      setIsLoading(true);

      // Prepare conversation history (last 10 messages for context)
      const history = [...messages, newUserMsg]
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }));

      // Start with empty assistant message
      let assistantContent = '';
      setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

      // Stream response
      const abort = streamChatMessage(
        userMessage.trim(),
        history.slice(0, -1), // Don't include the current message in history
        accessibilityMode,
        // onChunk
        (chunk) => {
          assistantContent += chunk;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: 'assistant',
              content: assistantContent,
            };
            return updated;
          });
        },
        // onDone
        () => {
          setIsLoading(false);
        },
        // onError
        (err) => {
          setIsLoading(false);
          setError('Failed to get a response. Please try again.');
          // Remove empty assistant message on error
          setMessages((prev) => {
            const updated = [...prev];
            if (updated[updated.length - 1]?.content === '') {
              updated.pop();
            }
            return updated;
          });
        },
      );

      abortRef.current = abort;
    },
    [messages, isLoading, accessibilityMode],
  );

  /**
   * Cancel an in-progress streaming response.
   */
  const cancelStream = useCallback(() => {
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
      setIsLoading(false);
    }
  }, []);

  /**
   * Clear all messages and start fresh.
   */
  const clearChat = useCallback(() => {
    cancelStream();
    setMessages([]);
    setError(null);
  }, [cancelStream]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    cancelStream,
    clearChat,
  };
}

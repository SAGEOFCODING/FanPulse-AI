/**
 * ChatInput — Text input with debounced send and keyboard support.
 * Enter to send, Shift+Enter for newline. Fully keyboard-accessible.
 */

import { useState, useRef, useCallback } from 'react';
import './ChatInput.css';

export default function ChatInput({ onSend, isLoading, disabled }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  const handleSend = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;

    onSend(trimmed);
    setInput('');

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [input, onSend, disabled]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e) => {
    setInput(e.target.value);

    // Auto-grow textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
  };

  return (
    <div className="chat-input-container" role="form" aria-label="Chat message input">
      <div className="chat-input-wrapper">
        <textarea
          ref={textareaRef}
          className="chat-input-field"
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything about the stadium..."
          disabled={disabled}
          rows={1}
          aria-label="Type your message"
          id="chat-input"
          maxLength={2000}
        />
        <button
          className="chat-send-btn"
          onClick={handleSend}
          disabled={!input.trim() || disabled}
          aria-label="Send message"
          id="send-message-btn"
        >
          {isLoading ? (
            <span className="send-loading" aria-label="Sending">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </span>
          ) : (
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M22 2L11 13" />
              <path d="M22 2L15 22L11 13L2 9L22 2Z" />
            </svg>
          )}
        </button>
      </div>
      <p className="chat-input-hint">
        Press <kbd>Enter</kbd> to send, <kbd>Shift + Enter</kbd> for new line
      </p>
    </div>
  );
}

/**
 * ChatWindow — Displays conversation messages with auto-scroll.
 * Renders user and assistant messages with proper styling and animations.
 */

import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import './ChatWindow.css';

export default function ChatWindow({ messages, isLoading, error, onClear }) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) return null;

  return (
    <section className="chat-window" role="log" aria-label="Chat conversation" aria-live="polite">
      {/* Clear Chat Button */}
      {messages.length > 0 && (
        <div className="chat-toolbar">
          <button
            className="btn btn-sm btn-secondary"
            onClick={onClear}
            aria-label="Clear conversation"
            id="clear-chat-btn"
          >
            <span aria-hidden="true">🗑️</span> Clear Chat
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            role={msg.role}
            content={msg.content}
            isStreaming={isLoading && index === messages.length - 1 && msg.role === 'assistant'}
          />
        ))}

        {/* Error message */}
        {error && (
          <div className="chat-error animate-fade-in" role="alert">
            <span aria-hidden="true">⚠️</span> {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </section>
  );
}

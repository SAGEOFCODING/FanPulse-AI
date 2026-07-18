/**
 * ChatMessage — Renders a single chat message (user or assistant).
 * Handles streaming indicator and markdown-like formatting.
 */

import './ChatMessage.css';

/**
 * Simple markdown-to-HTML renderer for chat responses.
 * Handles bold, headers, and lists without a heavy library.
 */
function formatMessageContent(content) {
  if (!content) return '';

  return (
    content
      // Bold: **text**
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Headers: ### text
      .replace(/^### (.+)$/gm, '<h4>$1</h4>')
      .replace(/^## (.+)$/gm, '<h3>$1</h3>')
      // List items: - text or * text
      .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
      // Numbered lists: 1. text
      .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
      // Line breaks
      .replace(/\n/g, '<br />')
  );
}

export default function ChatMessage({ role, content, isStreaming }) {
  const isUser = role === 'user';

  return (
    <article
      className={`chat-message ${isUser ? 'chat-message-user' : 'chat-message-assistant'} ${
        isStreaming ? 'streaming' : ''
      } animate-fade-in`}
      aria-label={`${isUser ? 'Your' : 'AI assistant'} message`}
    >
      {/* Avatar */}
      <div className="chat-message-avatar" aria-hidden="true">
        {isUser ? '👤' : '⚡'}
      </div>

      {/* Content */}
      <div className="chat-message-content">
        <span className="chat-message-role">{isUser ? 'You' : 'FanPulse AI'}</span>
        <div
          className="chat-message-text"
          dangerouslySetInnerHTML={{ __html: formatMessageContent(content) }}
        />
        {isStreaming && (
          <span className="chat-streaming-indicator" aria-label="AI is responding">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </span>
        )}
      </div>
    </article>
  );
}

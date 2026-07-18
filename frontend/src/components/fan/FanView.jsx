/**
 * FanView — Main fan-facing page with AI concierge chat.
 * Includes quick-action buttons, chat interface, and accessibility mode.
 */

import { useChat } from '../../hooks/useChat';
import ChatWindow from './ChatWindow';
import ChatInput from './ChatInput';
import './FanView.css';

const QUICK_ACTIONS = [
  {
    id: 'find-seat',
    label: 'Find my seat',
    icon: '💺',
    message: "How do I find my seat? I'm in Section 114.",
  },
  {
    id: 'nearest-restroom',
    label: 'Nearest restroom',
    icon: '🚻',
    message: 'Where is the nearest restroom to my location?',
  },
  {
    id: 'shuttle-schedule',
    label: 'Shuttle schedule',
    icon: '🚌',
    message: 'What are the shuttle schedules back to the city after the match?',
  },
  {
    id: 'water-refill',
    label: 'Water refill',
    icon: '💧',
    message: 'Where is the nearest water refill station?',
  },
  {
    id: 'accessibility',
    label: 'Accessibility help',
    icon: '♿',
    message:
      'I need wheelchair accessibility information. What routes and elevators are available?',
  },
  {
    id: 'prayer-room',
    label: 'Prayer room',
    icon: '🕌',
    message: 'Where are the prayer rooms located in the stadium?',
  },
];

export default function FanView({ accessibilityMode }) {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat(accessibilityMode);

  const handleQuickAction = (action) => {
    sendMessage(action.message);
  };

  return (
    <main className="fan-view page-container" role="main" aria-label="Fan AI Concierge">
      {/* Welcome Section */}
      {messages.length === 0 && (
        <section className="fan-welcome animate-fade-in" aria-label="Welcome">
          <div className="fan-welcome-content">
            <h2 className="fan-welcome-title">
              <span className="gradient-text">Welcome to the Stadium</span>
            </h2>
            <p className="fan-welcome-subtitle">
              I&apos;m your AI concierge — ask me about directions, facilities, transport,
              accessibility, or anything about the venue. I speak your language!
            </p>

            {/* Quick Actions */}
            <div className="quick-actions" role="group" aria-label="Quick action buttons">
              {QUICK_ACTIONS.map((action) => (
                <button
                  key={action.id}
                  className="quick-action-btn"
                  onClick={() => handleQuickAction(action)}
                  aria-label={action.label}
                  id={`quick-action-${action.id}`}
                >
                  <span className="quick-action-icon" aria-hidden="true">
                    {action.icon}
                  </span>
                  <span className="quick-action-label">{action.label}</span>
                </button>
              ))}
            </div>

            {/* Multilingual Hint */}
            <div className="fan-multilingual-hint" aria-label="Multilingual support">
              <p>
                <span aria-hidden="true">🌍</span> Speak in any language — I&apos;ll respond in
                yours
              </p>
              <div className="fan-languages">
                <span>English</span>
                <span>Español</span>
                <span>Français</span>
                <span>Português</span>
                <span>العربية</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Chat Window */}
      <ChatWindow messages={messages} isLoading={isLoading} error={error} onClear={clearChat} />

      {/* Chat Input */}
      <ChatInput onSend={sendMessage} isLoading={isLoading} disabled={isLoading} />
    </main>
  );
}

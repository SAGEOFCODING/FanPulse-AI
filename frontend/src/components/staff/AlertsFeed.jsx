/**
 * AlertsFeed — Displays real-time operational alerts sorted by severity.
 * Shows severity badges with timestamps for each alert.
 */

import './AlertsFeed.css';

export default function AlertsFeed({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="alerts-empty">
        <span className="alerts-empty-icon" aria-hidden="true">
          ✅
        </span>
        <p>All systems normal — no active alerts</p>
      </div>
    );
  }

  // Sort: critical first, then warning, then info
  const sortedAlerts = [...alerts].sort((a, b) => {
    const order = { critical: 0, warning: 1, info: 2 };
    return (order[a.severity] ?? 3) - (order[b.severity] ?? 3);
  });

  return (
    <ul className="alerts-list" aria-label="Operational alerts list">
      {sortedAlerts.map((alert, index) => (
        <li
          key={`${alert.gate_id}-${index}`}
          className={`alert-item alert-${alert.severity} animate-fade-in`}
          role="alert"
          style={{ animationDelay: `${index * 0.05}s` }}
        >
          <div className="alert-header">
            <span className={`badge badge-${alert.severity}`}>{alert.severity}</span>
            <span className="alert-gate">Gate {alert.gate_id}</span>
            <time className="alert-time" dateTime={alert.timestamp}>
              {new Date(alert.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </time>
          </div>
          <p className="alert-message">{alert.message}</p>
        </li>
      ))}
    </ul>
  );
}

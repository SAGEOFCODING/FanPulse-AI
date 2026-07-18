/**
 * Header component — persistent navigation bar with role switcher and accessibility controls.
 */

import { useLocation, Link } from 'react-router-dom';
import './Header.css';

export default function Header({ highContrast, largeText, toggleHighContrast, toggleLargeText }) {
  const location = useLocation();
  const isStaff = location.pathname.startsWith('/staff');

  return (
    <header className="header" role="banner">
      <div className="header-inner">
        {/* Logo & Title */}
        <Link to="/" className="header-brand" aria-label="FanPulse AI Home">
          <span className="header-logo" aria-hidden="true">
            ⚡
          </span>
          <div className="header-title-group">
            <h1 className="header-title">
              <span className="gradient-text">FanPulse</span>{' '}
              <span className="header-title-ai">AI</span>
            </h1>
            <span className="header-subtitle">FIFA World Cup 2026</span>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="header-nav" role="navigation" aria-label="Main navigation">
          <Link
            to="/fan"
            className={`header-nav-link ${!isStaff ? 'active' : ''}`}
            aria-current={!isStaff ? 'page' : undefined}
            id="nav-fan-view"
          >
            <span aria-hidden="true">🏟️</span>
            <span>Fan View</span>
          </Link>
          <Link
            to="/staff"
            className={`header-nav-link ${isStaff ? 'active' : ''}`}
            aria-current={isStaff ? 'page' : undefined}
            id="nav-staff-view"
          >
            <span aria-hidden="true">📊</span>
            <span>Staff View</span>
          </Link>
        </nav>

        {/* Accessibility Controls */}
        <div className="header-a11y" role="group" aria-label="Accessibility settings">
          <button
            className={`btn-icon a11y-toggle ${highContrast ? 'active' : ''}`}
            onClick={toggleHighContrast}
            aria-pressed={highContrast}
            aria-label="Toggle high contrast mode"
            title="High contrast mode"
            id="toggle-high-contrast"
          >
            <span aria-hidden="true">◐</span>
          </button>
          <button
            className={`btn-icon a11y-toggle ${largeText ? 'active' : ''}`}
            onClick={toggleLargeText}
            aria-pressed={largeText}
            aria-label="Toggle large text mode"
            title="Large text mode"
            id="toggle-large-text"
          >
            <span aria-hidden="true">Aa</span>
          </button>
        </div>
      </div>
    </header>
  );
}

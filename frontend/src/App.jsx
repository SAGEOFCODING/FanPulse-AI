/**
 * FanPulse AI — Main Application Component
 *
 * Single React app with role-based routes:
 * - /fan → Fan AI Concierge view
 * - /staff → Staff Operations Command Center
 *
 * Accessibility settings (high contrast, large text) are managed
 * at this level and passed down to child components.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAccessibility } from './hooks/useAccessibility';
import Header from './components/common/Header';
import FanView from './components/fan/FanView';
import StaffView from './components/staff/StaffView';

export default function App() {
  const { highContrast, largeText, toggleHighContrast, toggleLargeText, accessibilityMode } =
    useAccessibility();

  return (
    <BrowserRouter>
      <div className="app">
        <Header
          highContrast={highContrast}
          largeText={largeText}
          toggleHighContrast={toggleHighContrast}
          toggleLargeText={toggleLargeText}
        />
        <Routes>
          <Route path="/fan" element={<FanView accessibilityMode={accessibilityMode} />} />
          <Route path="/staff" element={<StaffView />} />
          {/* Redirect root to fan view */}
          <Route path="*" element={<Navigate to="/fan" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

/**
 * SummaryReport — Modal overlay displaying AI-generated shift summary.
 * Triggered by the "Shift Summary" button on the staff dashboard.
 */

import { useEffect, useRef } from 'react';
import './SummaryReport.css';

export default function SummaryReport({ summary, onClose }) {
  const modalRef = useRef(null);
  const closeButtonRef = useRef(null);

  // Focus trap and ESC key handling
  useEffect(() => {
    closeButtonRef.current?.focus();

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div
      className="summary-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Shift summary report"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="summary-modal glass-card animate-fade-in" ref={modalRef}>
        {/* Header */}
        <div className="summary-header">
          <h3 className="summary-title">
            <span aria-hidden="true">📋</span> Shift Summary Report
          </h3>
          <button
            ref={closeButtonRef}
            className="btn-icon summary-close"
            onClick={onClose}
            aria-label="Close summary report"
            id="close-summary-btn"
          >
            ✕
          </button>
        </div>

        {/* Meta */}
        <div className="summary-meta">
          <span className="summary-meta-item">
            <strong>Duration:</strong> {summary.shift_duration_minutes} minutes
          </span>
          <span className="summary-meta-item">
            <strong>Data points:</strong> {summary.data_points_analyzed}
          </span>
          <span className="badge badge-info">AI Generated</span>
        </div>

        {/* Content */}
        <div className="summary-content">{summary.summary}</div>

        {/* Footer */}
        <div className="summary-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

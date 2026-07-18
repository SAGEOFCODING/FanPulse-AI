/**
 * StaffView — Operations Command Center dashboard.
 * Shows crowd heatmap, AI-generated alerts, and shift summary tools.
 * Auto-refreshes crowd data every 10 seconds.
 */

import { useState, useEffect, useCallback } from 'react';
import { getCrowdData, getAlerts, analyzecrowd, generateShiftSummary } from '../../services/api';
import CrowdHeatmap from './CrowdHeatmap';
import AlertsFeed from './AlertsFeed';
import SummaryReport from './SummaryReport';
import './StaffView.css';

export default function StaffView() {
  const [crowdData, setCrowdData] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [summary, setSummary] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [error, setError] = useState(null);

  // Fetch crowd data and alerts
  const fetchData = useCallback(async () => {
    try {
      const [crowdRes, alertsRes] = await Promise.all([getCrowdData(), getAlerts()]);
      setCrowdData(crowdRes);
      setAlerts(alertsRes);
      setError(null);
    } catch (err) {
      setError('Unable to fetch operational data. Check backend connection.');
    }
  }, []);

  // Initial fetch + auto-refresh every 10 seconds
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Request AI analysis
  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const result = await analyzecrowd(30);
      setAnalysis(result);
    } catch (err) {
      setError('Failed to generate AI analysis.');
    }
    setIsAnalyzing(false);
  };

  // Generate shift summary
  const handleGenerateSummary = async () => {
    setIsGeneratingSummary(true);
    try {
      const result = await generateShiftSummary(60);
      setSummary(result);
      setShowSummary(true);
    } catch (err) {
      setError('Failed to generate shift summary.');
    }
    setIsGeneratingSummary(false);
  };

  return (
    <main className="staff-view page-container" role="main" aria-label="Operations Command Center">
      {/* Header Bar */}
      <section className="staff-header">
        <div className="staff-header-left">
          <h2 className="staff-title">
            <span className="gradient-text">Command Center</span>
          </h2>
          <p className="staff-subtitle">
            Real-time operational intelligence — all data is simulated
          </p>
        </div>
        <div className="staff-header-actions">
          <button
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            id="analyze-crowd-btn"
            aria-label="Request AI crowd analysis"
          >
            {isAnalyzing ? 'Analyzing...' : '🤖 AI Analysis'}
          </button>
          <button
            className="btn btn-accent"
            onClick={handleGenerateSummary}
            disabled={isGeneratingSummary}
            id="generate-summary-btn"
            aria-label="Generate shift summary report"
          >
            {isGeneratingSummary ? 'Generating...' : '📋 Shift Summary'}
          </button>
        </div>
      </section>

      {/* Error Banner */}
      {error && (
        <div className="staff-error" role="alert">
          <span aria-hidden="true">⚠️</span> {error}
        </div>
      )}

      {/* Dashboard Grid */}
      <div className="staff-dashboard">
        {/* Left: Heatmap */}
        <section
          className="staff-panel heatmap-panel glass-card"
          aria-label="Crowd density heatmap"
        >
          <h3 className="panel-title">Crowd Density Map</h3>
          {crowdData ? (
            <CrowdHeatmap gates={crowdData.gates} />
          ) : (
            <div className="skeleton" style={{ height: '400px' }} />
          )}

          {/* Weather Strip */}
          {crowdData?.weather && (
            <div className="weather-strip" aria-label="Current weather conditions">
              <span className="weather-item">
                <span aria-hidden="true">🌡️</span> {crowdData.weather.temperature_celsius}°C
              </span>
              <span className="weather-item">
                <span aria-hidden="true">☁️</span> {crowdData.weather.condition}
              </span>
              <span className="weather-item">
                <span aria-hidden="true">💨</span> {crowdData.weather.wind_speed_kmh} km/h
              </span>
              <span className="weather-item">
                <span aria-hidden="true">💧</span> {crowdData.weather.humidity_percent}%
              </span>
              {crowdData.weather.heat_advisory && (
                <span className="badge badge-warning">Heat Advisory</span>
              )}
            </div>
          )}

          {/* Stats Strip */}
          {crowdData?.summary && (
            <div className="stats-strip" aria-label="Crowd statistics summary">
              <div className="stat-item">
                <span className="stat-value">
                  {crowdData.summary.total_estimated_fans?.toLocaleString()}
                </span>
                <span className="stat-label">Est. Fans</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{crowdData.summary.average_density_percent}%</span>
                <span className="stat-label">Avg. Density</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{crowdData.summary.busiest_gate}</span>
                <span className="stat-label">Busiest Gate</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{crowdData.summary.quietest_gate}</span>
                <span className="stat-label">Quietest Gate</span>
              </div>
            </div>
          )}
        </section>

        {/* Right: Alerts + Analysis */}
        <div className="staff-right-col">
          {/* Alerts */}
          <section className="staff-panel alerts-panel glass-card" aria-label="Operational alerts">
            <h3 className="panel-title">
              Active Alerts
              {alerts && (
                <span className="alert-count-badges">
                  {alerts.critical_count > 0 && (
                    <span className="badge badge-critical">{alerts.critical_count} Critical</span>
                  )}
                  {alerts.warning_count > 0 && (
                    <span className="badge badge-warning">{alerts.warning_count} Warning</span>
                  )}
                </span>
              )}
            </h3>
            {alerts ? (
              <AlertsFeed alerts={alerts.alerts} />
            ) : (
              <div className="skeleton" style={{ height: '200px' }} />
            )}
          </section>

          {/* AI Analysis Results */}
          {analysis && (
            <section
              className="staff-panel analysis-panel glass-card animate-fade-in"
              aria-label="AI analysis results"
            >
              <h3 className="panel-title">
                <span aria-hidden="true">🤖</span> AI Analysis
              </h3>
              <div className="analysis-content">{analysis.analysis}</div>
            </section>
          )}
        </div>
      </div>

      {/* Summary Modal */}
      {showSummary && summary && (
        <SummaryReport summary={summary} onClose={() => setShowSummary(false)} />
      )}
    </main>
  );
}

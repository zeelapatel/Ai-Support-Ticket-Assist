import React, { useState, useEffect, useRef, useCallback } from 'react';
import { getAllAnalysisRuns } from '../services/api';
import './AnalysisSidebar.css';

function AnalysisSidebar({ onAnalysisSelect, selectedRunId, refreshTrigger }) {
  const [analysisRuns, setAnalysisRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAutoRefreshing, setIsAutoRefreshing] = useState(false);
  const intervalRef = useRef(null);
  const lastCountRef = useRef(0);

  // Load analysis runs
  const loadAnalysisRuns = useCallback(async (silent = false) => {
    try {
      if (!silent) {
        setLoading(true);
      } else {
        setIsAutoRefreshing(true);
      }
      setError(null);
      const data = await getAllAnalysisRuns();
      
      // Check if new analysis was added
      if (data.length > lastCountRef.current && lastCountRef.current > 0) {
        // New analysis detected - could show a notification here
        console.log('New analysis detected!');
      }
      lastCountRef.current = data.length;
      
      setAnalysisRuns(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load analysis history');
      console.error('Error loading analysis runs:', err);
    } finally {
      setLoading(false);
      setIsAutoRefreshing(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadAnalysisRuns();
  }, [loadAnalysisRuns]);

  // Auto-refresh when refreshTrigger changes (new analysis created)
  useEffect(() => {
    if (refreshTrigger !== undefined && refreshTrigger > 0) {
      loadAnalysisRuns(true); // Silent refresh
    }
  }, [refreshTrigger, loadAnalysisRuns]);

  // Periodic auto-refresh every 30 seconds
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      loadAnalysisRuns(true); // Silent refresh
    }, 30000); // 30 seconds

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [loadAnalysisRuns]);

  const handleRunClick = (run) => {
    if (onAnalysisSelect) {
      onAnalysisSelect(run.id);
    }
  };

  const handleManualRefresh = () => {
    loadAnalysisRuns(false); // Show loading indicator
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateSummary = (summary, maxLength = 80) => {
    if (!summary) return 'No summary';
    if (summary.length <= maxLength) return summary;
    return summary.substring(0, maxLength) + '...';
  };

  return (
    <div className="analysis-sidebar">
      <div className="sidebar-header">
        <h2>Analysis History</h2>
        <div className="header-actions">
          {isAutoRefreshing && (
            <span className="auto-refresh-indicator" title="Auto-refreshing...">
              ⟳
            </span>
          )}
          <button 
            className={`refresh-btn ${loading ? 'refreshing' : ''}`}
            onClick={handleManualRefresh}
            title="Refresh history"
            disabled={loading}
          >
            ↻
          </button>
        </div>
      </div>

      <div className="sidebar-content">
        {loading && analysisRuns.length === 0 ? (
          <div className="sidebar-loading">
            <div className="spinner"></div>
            <p>Loading...</p>
          </div>
        ) : error ? (
          <div className="sidebar-error">{error}</div>
        ) : analysisRuns.length === 0 ? (
          <div className="sidebar-empty">
            <p>No analysis history yet.</p>
            <p className="empty-hint">Run an analysis to see results here.</p>
          </div>
        ) : (
          <div className="runs-list">
            {analysisRuns.map((run) => (
              <div
                key={run.id}
                className={`run-item ${selectedRunId === run.id ? 'selected' : ''}`}
                onClick={() => handleRunClick(run)}
              >
                <div className="run-item-header">
                  <span className="run-id">#{run.id}</span>
                  <span className="run-date">{formatDate(run.created_at)}</span>
                </div>
                <div className="run-summary">
                  {truncateSummary(run.summary)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalysisSidebar;


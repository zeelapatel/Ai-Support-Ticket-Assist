import React, { useState, useEffect } from 'react';
import { getAllAnalysisRuns, getAnalysisById } from '../services/api';
import AnalysisResults from './AnalysisResults';
import './AnalysisHistory.css';

function AnalysisHistory({ onAnalysisSelect }) {
  const [analysisRuns, setAnalysisRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (isExpanded) {
      loadAnalysisRuns();
    }
  }, [isExpanded]);

  const loadAnalysisRuns = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAllAnalysisRuns();
      setAnalysisRuns(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load analysis history');
      console.error('Error loading analysis runs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunClick = async (runId) => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAnalysisById(runId);
      setSelectedRun(runId);
      setSelectedAnalysis(data);
      
      // Notify parent component if callback provided
      if (onAnalysisSelect) {
        onAnalysisSelect(data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load analysis');
      console.error('Error loading analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateSummary = (summary, maxLength = 100) => {
    if (!summary) return 'No summary available';
    if (summary.length <= maxLength) return summary;
    return summary.substring(0, maxLength) + '...';
  };

  return (
    <div className="analysis-history-container">
      <div className="history-header">
        <h2>Analysis History</h2>
        <button
          className="toggle-btn"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>

      {isExpanded && (
        <div className="history-content">
          {loading && analysisRuns.length === 0 ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading analysis history...</p>
            </div>
          ) : error ? (
            <div className="error-message">{error}</div>
          ) : analysisRuns.length === 0 ? (
            <div className="empty-state">
              <p>No analysis history yet. Run an analysis to see results here.</p>
            </div>
          ) : (
            <>
              <div className="runs-list">
                {analysisRuns.map((run) => (
                  <div
                    key={run.id}
                    className={`run-item ${selectedRun === run.id ? 'selected' : ''}`}
                    onClick={() => handleRunClick(run.id)}
                  >
                    <div className="run-header">
                      <span className="run-id">Run #{run.id}</span>
                      <span className="run-date">{formatDate(run.created_at)}</span>
                    </div>
                    <div className="run-summary">
                      {truncateSummary(run.summary)}
                    </div>
                  </div>
                ))}
              </div>

              {selectedAnalysis && (
                <div className="selected-analysis">
                  <div className="selected-analysis-header">
                    <h3>Selected Analysis - Run #{selectedAnalysis.analysis_run.id}</h3>
                    <button
                      className="close-btn"
                      onClick={() => {
                        setSelectedAnalysis(null);
                        setSelectedRun(null);
                      }}
                    >
                      ×
                    </button>
                  </div>
                  <AnalysisResults analysis={selectedAnalysis} />
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default AnalysisHistory;


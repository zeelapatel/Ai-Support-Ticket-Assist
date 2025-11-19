import React from 'react';
import './AnalysisResults.css';

function AnalysisResults({ analysis }) {
  if (!analysis) {
    return null;
  }

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return '#ff4757';
      case 'high':
        return '#ff6b6b';
      case 'medium':
        return '#ffa502';
      case 'low':
        return '#2ed573';
      default:
        return '#888';
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      billing: '#667eea',
      bug: '#ff4757',
      feature_request: '#2ed573',
      account: '#ffa502',
      technical: '#5f27cd',
      other: '#888',
    };
    return colors[category?.toLowerCase()] || colors.other;
  };

  return (
    <div className="analysis-results-container">
      <h2>Analysis Results</h2>
      
      {analysis.analysis_run && (
        <div className="analysis-summary">
          <h3>Summary</h3>
          <p>{analysis.analysis_run.summary || 'No summary available'}</p>
          <div className="analysis-meta">
            <span>Run ID: {analysis.analysis_run.id}</span>
            <span>
              {new Date(analysis.analysis_run.created_at).toLocaleString()}
            </span>
          </div>
        </div>
      )}

      {analysis.ticket_analyses && analysis.ticket_analyses.length > 0 && (
        <div className="ticket-analyses">
          <h3>Ticket Analysis ({analysis.ticket_analyses.length})</h3>
          <div className="analyses-list">
            {analysis.ticket_analyses.map((ta) => (
              <div key={ta.id} className="analysis-item">
                <div className="analysis-header">
                  <h4>
                    {ta.ticket?.title || `Ticket #${ta.ticket_id}`}
                  </h4>
                  <div className="analysis-badges">
                    {ta.category && (
                      <span
                        className="badge category-badge"
                        style={{ backgroundColor: getCategoryColor(ta.category) }}
                      >
                        {ta.category}
                      </span>
                    )}
                    {ta.priority && (
                      <span
                        className="badge priority-badge"
                        style={{ backgroundColor: getPriorityColor(ta.priority) }}
                      >
                        {ta.priority}
                      </span>
                    )}
                  </div>
                </div>
                
                {ta.ticket?.description && (
                  <p className="ticket-description">{ta.ticket.description}</p>
                )}
                
                {ta.notes && (
                  <div className="analysis-notes">
                    <strong>Notes:</strong> {ta.notes}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalysisResults;


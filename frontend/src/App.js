import React, { useState, useEffect } from 'react';
import { getTickets, analyzeTickets, getLatestAnalysis } from './services/api';
import TicketForm from './components/TicketForm';
import TicketList from './components/TicketList';
import AnalysisResults from './components/AnalysisResults';
import './App.css';

function App() {
  const [tickets, setTickets] = useState([]);
  const [selectedTickets, setSelectedTickets] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  // Load tickets on mount
  useEffect(() => {
    loadTickets();
    loadLatestAnalysis();
  }, []);

  const loadTickets = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTickets();
      setTickets(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load tickets');
      console.error('Error loading tickets:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadLatestAnalysis = async () => {
    try {
      const data = await getLatestAnalysis();
      setAnalysis(data);
    } catch (err) {
      // It's okay if there's no analysis yet
      if (err.response?.status !== 404) {
        console.error('Error loading analysis:', err);
      }
    }
  };

  const handleTicketCreated = () => {
    loadTickets();
  };

  const handleTicketSelect = (ticketId) => {
    setSelectedTickets((prev) =>
      prev.includes(ticketId)
        ? prev.filter((id) => id !== ticketId)
        : [...prev, ticketId]
    );
  };

  const handleSelectAll = () => {
    setSelectedTickets(tickets.map((t) => t.id));
  };

  const handleDeselectAll = () => {
    setSelectedTickets([]);
  };

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      setError(null);
      
      // Determine which tickets to analyze
      const ticketIds = selectedTickets.length > 0 ? selectedTickets : null;
      
      // Call analyze API
      const result = await analyzeTickets(ticketIds);
      
      // Reload tickets and analysis
      await loadTickets();
      await loadLatestAnalysis();
      
      // Clear selection
      setSelectedTickets([]);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to analyze tickets');
      console.error('Error analyzing tickets:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Support Ticket Assist</h1>
        <p className="subtitle">Intelligent ticket analysis and management</p>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="close-error">×</button>
          </div>
        )}

        <TicketForm onTicketCreated={handleTicketCreated} />

        <div className="action-section">
          <button
            onClick={handleAnalyze}
            className="analyze-btn"
            disabled={analyzing || tickets.length === 0}
          >
            {analyzing ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                {selectedTickets.length > 0
                  ? `Analyze Selected (${selectedTickets.length})`
                  : 'Analyze All Tickets'}
              </>
            )}
          </button>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading tickets...</p>
          </div>
        ) : (
          <TicketList
            tickets={tickets}
            selectedTickets={selectedTickets}
            onTicketSelect={handleTicketSelect}
            onSelectAll={handleSelectAll}
            onDeselectAll={handleDeselectAll}
          />
        )}

        {analysis && <AnalysisResults analysis={analysis} />}
      </main>
    </div>
  );
}

export default App;

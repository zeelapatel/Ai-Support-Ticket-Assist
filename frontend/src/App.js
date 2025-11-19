import React, { useState, useEffect } from 'react';
import { healthCheck } from './services/api';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check API health on component mount
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const status = await healthCheck();
      setApiStatus(status);
    } catch (err) {
      setError(err.message);
      setApiStatus(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Support Ticket Assist</h1>
        <p className="subtitle">Intelligent ticket analysis and management</p>
      </header>

      <main className="App-main">
        <section className="status-section">
          <h2>API Status</h2>
          {loading && <p className="loading">Checking API connection...</p>}
          {error && (
            <div className="error">
              <p>Error: {error}</p>
              <button onClick={checkApiHealth} className="retry-btn">
                Retry Connection
              </button>
            </div>
          )}
          {apiStatus && !loading && (
            <div className="success">
              <p>✓ API is {apiStatus.status}</p>
              <p className="api-url">Connected to: {API_BASE_URL}</p>
            </div>
          )}
        </section>

        <section className="content-section">
          <h2>Welcome</h2>
          <p>This is the AI Support Ticket Assist application.</p>
          <p>Frontend is ready for development.</p>
        </section>
      </main>
    </div>
  );
}

export default App;


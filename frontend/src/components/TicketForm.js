import React, { useState } from 'react';
import './TicketForm.css';

function TicketForm({ onTicketCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title.trim() || !description.trim()) {
      setError('Please fill in both title and description');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const { createTickets } = await import('../services/api');
      await createTickets([{ title: title.trim(), description: description.trim() }]);
      
      // Reset form
      setTitle('');
      setDescription('');
      
      // Notify parent to refresh tickets
      if (onTicketCreated) {
        onTicketCreated();
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to create ticket');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ticket-form-container">
      <h2>Create New Ticket</h2>
      <form onSubmit={handleSubmit} className="ticket-form">
        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter ticket title"
            disabled={loading}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter ticket description"
            rows="4"
            disabled={loading}
            required
          />
        </div>

        {error && <div className="form-error">{error}</div>}

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Adding...' : 'Add Ticket'}
        </button>
      </form>
    </div>
  );
}

export default TicketForm;


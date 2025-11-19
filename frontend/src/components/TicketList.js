import React from 'react';
import './TicketList.css';

function TicketList({ tickets, selectedTickets, onTicketSelect, onSelectAll, onDeselectAll }) {
  if (!tickets || tickets.length === 0) {
    return (
      <div className="ticket-list-container">
        <h2>Tickets</h2>
        <div className="empty-state">
          <p>No tickets yet. Create your first ticket above!</p>
        </div>
      </div>
    );
  }

  const allSelected = tickets.length > 0 && tickets.every(t => selectedTickets.includes(t.id));
  const someSelected = selectedTickets.length > 0 && !allSelected;

  return (
    <div className="ticket-list-container">
      <div className="ticket-list-header">
        <h2>Tickets ({tickets.length})</h2>
        {tickets.length > 0 && (
          <div className="selection-controls">
            <button
              onClick={allSelected ? onDeselectAll : onSelectAll}
              className="select-btn"
            >
              {allSelected ? 'Deselect All' : 'Select All'}
            </button>
            {selectedTickets.length > 0 && (
              <span className="selected-count">
                {selectedTickets.length} selected
              </span>
            )}
          </div>
        )}
      </div>

      <div className="ticket-list">
        {tickets.map((ticket) => {
          const isSelected = selectedTickets.includes(ticket.id);
          const truncatedDescription =
            ticket.description.length > 150
              ? ticket.description.substring(0, 150) + '...'
              : ticket.description;

          return (
            <div
              key={ticket.id}
              className={`ticket-item ${isSelected ? 'selected' : ''}`}
              onClick={() => onTicketSelect(ticket.id)}
            >
              <div className="ticket-checkbox">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => onTicketSelect(ticket.id)}
                  onClick={(e) => e.stopPropagation()}
                />
              </div>
              <div className="ticket-content">
                <h3 className="ticket-title">{ticket.title}</h3>
                <p className="ticket-description">{truncatedDescription}</p>
                <div className="ticket-meta">
                  <span className="ticket-id">ID: {ticket.id}</span>
                  <span className="ticket-date">
                    {new Date(ticket.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TicketList;


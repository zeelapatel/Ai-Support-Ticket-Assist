-- Database schema

-- Initialize the Support Ticket Analyst database

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summary TEXT
);

CREATE TABLE IF NOT EXISTS ticket_analysis (
    id SERIAL PRIMARY KEY,
    analysis_run_id INTEGER REFERENCES analysis_runs(id) ON DELETE CASCADE,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    category TEXT,
    priority TEXT,
    notes TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_created_at ON analysis_runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ticket_analysis_run_id ON ticket_analysis(analysis_run_id);
CREATE INDEX IF NOT EXISTS idx_ticket_analysis_ticket_id ON ticket_analysis(ticket_id);

-- Insert some sample data for testing
INSERT INTO tickets (title, description) VALUES 
    ('Billing Issue - Overcharged', 'I was charged twice for my subscription this month. Please refund the duplicate charge.'),
    ('Login Bug - Cannot Access Account', 'The login page crashes when I try to enter my credentials. This is urgent as I need to access my data.'),
    ('Feature Request - Dark Mode', 'Would love to see a dark mode option added to the application for better user experience.'),
    ('Payment Failed - Need Help', 'My payment keeps failing even though my card is valid. Can someone help me troubleshoot this?'),
    ('Critical Bug - Data Loss', 'I lost all my saved work when the app crashed. This is extremely urgent and needs immediate attention.')
ON CONFLICT DO NOTHING;
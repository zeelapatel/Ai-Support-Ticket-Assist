import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens or headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error:', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API service functions
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getRoot = async () => {
  const response = await api.get('/');
  return response.data;
};

// Ticket endpoints
export const createTickets = async (tickets) => {
  const response = await api.post('/api/tickets', { tickets });
  return response.data;
};

export const getTickets = async (skip = 0, limit = 100) => {
  const response = await api.get('/api/tickets', {
    params: { skip, limit }
  });
  return response.data;
};

export const getTicket = async (ticketId) => {
  const response = await api.get(`/api/tickets/${ticketId}`);
  return response.data;
};

// Analysis endpoints
export const analyzeTickets = async (ticketIds = null) => {
  const body = ticketIds ? { ticket_ids: ticketIds } : {};
  const response = await api.post('/api/analyze', body);
  return response.data;
};

export const getLatestAnalysis = async () => {
  const response = await api.get('/api/analysis/latest');
  return response.data;
};

export default api;


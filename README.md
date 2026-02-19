# AI Support Ticket Assist

A full-stack application that uses AI (LangGraph) to analyze and categorize support tickets. Built with FastAPI, React, PostgreSQL, and LangGraph.

## Table of Contents

- [Quickstart](#quickstart)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [API Overview](#api-overview)
- [Architecture Notes](#architecture-notes)
- [Tradeoffs & Shortcuts](#tradeoffs--shortcuts)
- [Future Improvements](#future-improvements)

---

## Quickstart

### Prerequisites

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)

To verify you have Docker installed:
```bash
docker --version
docker compose version
```

### How to Run the Whole Project

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd Ai-Support-Ticket-Assist
   ```

2. **Set up environment variables** (optional - defaults work for local development):
   ```bash
   # Create .env file in the root directory (optional)
   # See Configuration section for details
   ```

3. **Start all services**:
   ```bash
   docker compose up --build
   ```

4. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs (Swagger UI)
   - **Database**: localhost:5432

5. **Stop the services**:
   ```bash
   docker compose down
   ```

   To also remove volumes (database data):
   ```bash
   docker compose down -v
   ```

### Default Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React application |
| Backend | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | Database server |

---

## Configuration

### Environment Variables

The application uses environment variables for configuration. These can be set in:
- `.env` file in the project root (not included in repo)
- Docker Compose environment variables (see `docker-compose.yml`)
- System environment variables

#### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@postgres:5432/support_tickets` | PostgreSQL connection string |
| `HOST` | `0.0.0.0` | Backend server host |
| `PORT` | `8000` | Backend server port |
| `DEBUG` | `true` | Enable debug mode (auto-reload) |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:80` | Allowed CORS origins (comma-separated) |
| `OPENAI_API_KEY` | (none) | OpenAI API key for LangGraph agent  |

#### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:8000` | Backend API base URL |

#### Database Environment Variables (PostgreSQL)

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `POSTGRES_DB` | `support_tickets` | Database name |

### Example .env File

Create a `.env` file in the project root (optional):

```env
# Backend Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/support_tickets
HOST=0.0.0.0
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:80

# OpenAI Configuration (optional - for real AI analysis)
OPENAI_API_KEY=your_openai_api_key_here

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

### How the Backend Connects to Postgres

The backend uses SQLAlchemy ORM to connect to PostgreSQL:

1. **Connection String**: Read from `DATABASE_URL` environment variable
2. **Connection Pool**: Configured with:
   - `pool_pre_ping=True` - Verifies connections before use
   - `pool_size=10` - Maintains 10 connections
   - `max_overflow=20` - Allows up to 20 additional connections
3. **Session Management**: Uses SQLAlchemy's `SessionLocal` for database sessions
4. **Auto-creation**: Tables are automatically created on startup via `database.create_tables()`

The connection is established when the FastAPI application starts, and sessions are managed per-request using FastAPI's dependency injection system.

### How LangGraph / LLM is Configured

#### With OpenAI API Key (Real AI Analysis)

If `OPENAI_API_KEY` is set:
- Uses `ChatOpenAI` from `langchain-openai`
- Model: `gpt-4o-mini` (cost-effective, fast)
- Temperature: `0.3` (balanced creativity/consistency)
- Analyzes each ticket individually with structured prompts
- Returns JSON-formatted responses with category, priority, and notes

#### Without API Key (Mock Analysis)

If `OPENAI_API_KEY` is **not** set:
- Uses keyword-based mock analysis function
- Categorizes based on keywords in title/description:
  - **Billing**: billing, charge, payment, refund, invoice, subscription
  - **Bug**: bug, crash, error, broken, not working, issue
  - **Feature Request**: feature, request, add, would like, suggest
  - **Account**: login, account, access, password, authentication
  - **Technical**: technical, server, api, integration
  - **Other**: default category
- Prioritizes based on urgency keywords:
  - **Critical**: critical, urgent, immediately, emergency, data loss
  - **High**: high, important, asap, soon
  - **Low**: low, minor, whenever
  - **Medium**: default priority

**To use real AI analysis**, set your OpenAI API key:
```bash
export OPENAI_API_KEY=sk-your-key-here
# Or add it to .env file
```

---

## API Overview

### Base URL

```
http://localhost:8000
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs

### Endpoints

#### Health Check

```http
GET /health
```

Returns service health status.

**Response:**
```json
{
  "status": "healthy"
}
```

#### Create Tickets

```http
POST /api/tickets
Content-Type: application/json
```

Creates one or more support tickets.

**Request Body:**
```json
{
  "tickets": [
    {
      "title": "Login Issue",
      "description": "Cannot log in to my account"
    },
    {
      "title": "Feature Request",
      "description": "Would like dark mode support"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "tickets": [
    {
      "id": 1,
      "title": "Login Issue",
      "description": "Cannot log in to my account",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "title": "Feature Request",
      "description": "Would like dark mode support",
      "created_at": "2024-01-15T10:30:01"
    }
  ]
}
```

#### Get All Tickets

```http
GET /api/tickets?skip=0&limit=100
```

Retrieves all tickets with pagination.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Login Issue",
    "description": "Cannot log in to my account",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

#### Get Single Ticket

```http
GET /api/tickets/{ticket_id}
```

Retrieves a specific ticket by ID.

**Response:**
```json
{
  "id": 1,
  "title": "Login Issue",
  "description": "Cannot log in to my account",
  "created_at": "2024-01-15T10:30:00"
}
```

#### Analyze Tickets

```http
POST /api/analyze
Content-Type: application/json
```

Analyzes tickets using the LangGraph agent. Can analyze all tickets or a specific subset.

**Request Body (optional):**
```json
{
  "ticket_ids": [1, 2, 3]
}
```

If `ticket_ids` is omitted or empty, analyzes all tickets.

**Response (201 Created):**
```json
{
  "analysis_run": {
    "id": 1,
    "created_at": "2024-01-15T10:35:00",
    "summary": "Analyzed 3 ticket(s). Categories: bug(2), feature_request(1). Priorities: high(1), medium(2)."
  },
  "ticket_analyses": [
    {
      "id": 1,
      "analysis_run_id": 1,
      "ticket_id": 1,
      "category": "account",
      "priority": "high",
      "notes": "Login issues are typically high priority as they block user access."
    },
    {
      "id": 2,
      "analysis_run_id": 1,
      "ticket_id": 2,
      "category": "feature_request",
      "priority": "medium",
      "notes": "Feature request for UI enhancement."
    }
  ]
}
```

#### Get Latest Analysis

```http
GET /api/analysis/latest
```

Retrieves the most recent analysis run with all ticket analyses and their associated ticket data.

**Response:**
```json
{
  "analysis_run": {
    "id": 1,
    "created_at": "2024-01-15T10:35:00",
    "summary": "Analyzed 3 ticket(s)..."
  },
  "ticket_analyses": [
    {
      "id": 1,
      "analysis_run_id": 1,
      "ticket_id": 1,
      "category": "account",
      "priority": "high",
      "notes": "Login issues are typically high priority...",
      "ticket": {
        "id": 1,
        "title": "Login Issue",
        "description": "Cannot log in to my account",
        "created_at": "2024-01-15T10:30:00"
      }
    }
  ]
}
```

### Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request (resource created)
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Architecture Notes

### Tech Choices

#### Backend
- **FastAPI**: Modern, fast Python web framework with automatic API documentation
- **SQLAlchemy**: ORM for database operations with type safety
- **LangGraph**: Framework for building stateful, multi-actor applications with LLMs
- **LangChain**: Integration with OpenAI and other LLM providers
- **PostgreSQL**: Robust relational database with ACID compliance

#### Frontend
- **React**: Component-based UI library for building interactive interfaces
- **Axios**: HTTP client for API communication
- **CSS**: Custom styling with component-scoped stylesheets

#### Infrastructure
- **Docker**: Containerization for consistent deployment
- **Docker Compose**: Multi-container orchestration
- **PostgreSQL 15**: Latest stable PostgreSQL version

### Directory Structure

```
Ai-Support-Ticket-Assist/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application and routes
│   │   ├── database.py          # SQLAlchemy models and connection
│   │   ├── crud.py              # Database CRUD operations
│   │   ├── schemas.py           # Pydantic request/response models
│   │   └── agent.py             # LangGraph agent implementation
│   ├── migrations/
│   │   └── init.sql             # Database schema and sample data
│   ├── Dockerfile               # Backend container definition
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js               # Main React component
│   │   ├── components/
│   │   │   ├── TicketForm.js    # Ticket creation form
│   │   │   ├── TicketList.js    # Ticket list with selection
│   │   │   └── AnalysisResults.js # Analysis results display
│   │   └── services/
│   │       └── api.js           # API client functions
│   ├── Dockerfile               # Frontend container definition
│   └── package.json             # Node.js dependencies
├── docker-compose.yml           # Multi-container orchestration
└── README.md                    # This file
```

### How the LangGraph Agent is Wired to Postgres

The agent follows a clean separation of concerns:

1. **API Layer** (`main.py`):
   - Receives analysis request
   - Fetches tickets from database via CRUD functions
   - Creates analysis run record
   - Calls agent function

2. **Agent Layer** (`agent.py`):
   - Receives tickets and run_id
   - Uses LangGraph to:
     - Analyze each ticket (categorize, prioritize, generate notes)
     - Generate overall summary
   - Returns structured results (no direct DB access)

3. **Database Layer** (`crud.py`):
   - Writes analysis results to database
   - Updates analysis run with summary
   - Handles all SQLAlchemy operations

**Flow Diagram:**
```
API Request → Fetch Tickets (CRUD) → Create Run (CRUD) 
  → Agent Analysis (LangGraph) → Write Results (CRUD) → Return Response
```

### LangGraph Agent Structure

The agent uses a simple but effective graph:

1. **State**: `AgentState` TypedDict containing:
   - `tickets`: List of tickets to analyze
   - `analysis_results`: List of analysis results
   - `summary`: Overall summary string
   - `run_id`: Analysis run ID

2. **Nodes**:
   - `analyze_tickets`: Processes each ticket through LLM/mock function
   - `generate_summary`: Aggregates results into overall summary

3. **Flow**:
   ```
   Entry → analyze_tickets → generate_summary → END
   ```

4. **Execution**: Synchronous `graph.invoke()` (could be async for better performance)

### Database Schema

#### Tables

**tickets**
- `id` (SERIAL PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `description` (TEXT NOT NULL)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

**analysis_runs**
- `id` (SERIAL PRIMARY KEY)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- `summary` (TEXT)

**ticket_analysis**
- `id` (SERIAL PRIMARY KEY)
- `analysis_run_id` (INTEGER FK → analysis_runs)
- `ticket_id` (INTEGER FK → tickets)
- `category` (TEXT)
- `priority` (TEXT)
- `notes` (TEXT)

#### Relationships
- One analysis_run has many ticket_analyses
- One ticket has many ticket_analyses (across different runs)
- Foreign keys with CASCADE delete

---
    - OpenAPI spec enhancements
    - Architecture decision records (ADRs)
    - Developer onboarding guide


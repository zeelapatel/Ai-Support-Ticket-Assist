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

## Tradeoffs & Design Decisions

**Completed in ~2 hours** (well under the 3-hour assignment constraint). This section explains the key technical decisions made throughout the project and the reasoning behind them:

### Architecture & Technology Choices

1. **FastAPI + SQLAlchemy + PostgreSQL**
   - **Decision**: Used FastAPI for async-capable Python backend with SQLAlchemy ORM
   - **Reasoning**: FastAPI provides automatic API documentation, type safety, and excellent performance. SQLAlchemy offers a clean ORM abstraction while maintaining flexibility. PostgreSQL was chosen for its reliability and ACID compliance, essential for ticket analysis data integrity.

2. **React Frontend with Component-Based Architecture**
   - **Decision**: Built React app with separate components (TicketForm, TicketList, AnalysisResults, AnalysisSidebar)
   - **Reasoning**: Component-based architecture promotes reusability and maintainability. Separated concerns allow for easier testing and future enhancements. The modular structure made it easy to add features like resizable panels and analysis history.

3. **LangGraph for Agent Implementation**
   - **Decision**: Used LangGraph's StateGraph for the analysis agent
   - **Reasoning**: LangGraph provides a clear, visual way to structure agent workflows. The state-based approach makes it easy to understand the flow (analyze tickets → generate summary) and allows for future expansion with additional nodes. The separation between graph logic and database operations maintains clean architecture.

### Implementation Decisions

4. **Synchronous Agent Execution (`graph.invoke()` vs `graph.ainvoke()`)**
   - **Decision**: Used synchronous `graph.invoke()` instead of async `graph.ainvoke()`
   - **Reasoning**: While FastAPI supports async, the LangGraph agent processes tickets sequentially anyway. Using sync execution simplified error handling and debugging during the 2-hour timeframe. The performance difference is minimal for the expected ticket volumes, and async can be added later if needed.

5. **Mock Analysis Fallback**
   - **Decision**: Implemented keyword-based mock analysis when OpenAI API key is not available
   - **Reasoning**: This allows the application to be fully functional without external dependencies, making it easier to test and demonstrate. The mock implementation uses simple keyword matching, which is transparent and easy to understand. This decision prioritizes accessibility and testing over sophisticated fallback logic.

6. **Direct SQLAlchemy Table Creation**
   - **Decision**: Used `Base.metadata.create_all()` for table creation instead of Alembic migrations
   - **Reasoning**: For a 2-hour MVP, migration tooling adds complexity without immediate benefit. The SQL migration file (`init.sql`) exists for Docker initialization, providing the schema definition. Alembic migrations would be the next step for production, but weren't necessary for the initial implementation.

7. **Analysis History with Polling vs WebSockets**
   - **Decision**: Implemented 30-second polling for auto-refresh instead of WebSockets
   - **Reasoning**: Polling is simpler to implement, requires no additional infrastructure, and works reliably across all environments. For the expected usage patterns, 30-second refresh is sufficient. WebSockets would add complexity (connection management, reconnection logic) without significant benefit for this use case. Can be upgraded later if real-time updates become critical.

8. **Resizable Panels Implementation**
   - **Decision**: Built custom ResizableSplitter component instead of using a library
   - **Reasoning**: Custom implementation gives full control over behavior and styling. The component is lightweight (~80 lines) and tailored to our specific needs. Using a library would add dependencies and potential over-engineering for a simple splitter. The implementation uses native browser events for better performance.

9. **Sidebar Layout for Analysis History**
   - **Decision**: Placed analysis history in a left sidebar instead of a dropdown or modal
   - **Reasoning**: Sidebar provides persistent visibility of analysis history, making it easy to switch between analyses. This improves UX by reducing clicks and providing context. The collapsible design (though we kept it always visible) allows for future customization. This decision prioritizes discoverability and ease of use.

10. **Auto-refresh on Analysis Creation**
    - **Decision**: Implemented immediate refresh trigger when new analysis is created, plus periodic polling
    - **Reasoning**: Immediate refresh ensures users see new analyses right away without waiting for the next poll cycle. Combined with periodic polling, this provides both responsiveness and reliability. The dual approach handles both user-initiated actions and external changes.

### Code Organization Decisions

11. **Separation of Concerns (API → Agent → CRUD)**
    - **Decision**: Strict separation between API layer, agent logic, and database operations
    - **Reasoning**: This architecture makes the codebase maintainable and testable. Each layer has a single responsibility, making it easier to modify or replace components. For example, the agent can be tested independently of the database, and the API layer can be swapped without affecting business logic.

12. **Pydantic Schemas for Request/Response Validation**
    - **Decision**: Used Pydantic models for all API request/response validation
    - **Reasoning**: Pydantic provides automatic validation, type checking, and documentation. This catches errors early and ensures data consistency. The schemas also serve as documentation for API consumers, reducing the need for separate API docs.

13. **Error Handling Strategy**
    - **Decision**: Basic try/except blocks with logging, no retry logic or circuit breakers
    - **Reasoning**: For a 2-hour MVP, comprehensive error handling would consume significant time. Basic error handling with logging provides visibility into issues. Retry logic and circuit breakers are important for production but can be added incrementally. The current approach prioritizes getting core functionality working.

### What Was Prioritized

1. ✅ **Core Functionality First**: All required endpoints and features implemented
2. ✅ **Code Quality**: Clean architecture and separation of concerns maintained
3. ✅ **User Experience**: Added bonus features (history, resizable panels) that enhance usability
4. ✅ **Docker Setup**: Ensured easy deployment and reproducibility
5. ✅ **Documentation**: Comprehensive README to help reviewers understand the project

### What Was Deferred (And Why)

1. **Comprehensive Testing**: Testing would require significant time. Manual testing was sufficient for MVP validation, and automated tests can be added incrementally.

2. **Production-Ready Error Handling**: Retry logic, circuit breakers, and advanced error recovery are important but not critical for demonstrating core functionality.

3. **Rate Limiting & Security Hardening**: These are production concerns that can be added when moving beyond MVP stage.

4. **Database Migrations (Alembic)**: The current approach works for initial deployment. Migrations become critical when schema changes are needed in production.

5. **WebSockets for Real-Time Updates**: Polling is sufficient for current needs. WebSockets add complexity that wasn't justified for the MVP.

**Note**: All deferred items are well-understood and can be implemented incrementally. The current architecture supports adding these features without major refactoring.

---

## Future Improvements

If given more time, here's what would be prioritized:

### High Priority

1. **Testing**
   - Unit tests for CRUD operations
   - Integration tests for API endpoints
   - Agent testing with mocked LLM responses
   - Frontend component tests

2. **Error Handling & Resilience**
   - Retry logic for database connections
   - Circuit breakers for external API calls
   - Better error messages for users
   - Error tracking (Sentry, etc.)

3. **Security**
   - Input validation and sanitization
   - Rate limiting (per IP/user)
   - API authentication/authorization
   - SQL injection prevention (already handled by SQLAlchemy, but audit)

4. **Database Migrations**
   - Alembic for schema versioning
   - Migration rollback support
   - Data migration scripts

### Medium Priority

5. **Performance**
   - Async agent execution (`graph.ainvoke()`)
   - Database query optimization
   - Caching for frequently accessed data
   - Pagination improvements

6. **Monitoring & Observability**
   - Structured logging
   - Metrics collection (Prometheus)
   - Health check improvements
   - Request tracing

7. **UI/UX Enhancements**
   - Real-time updates (WebSockets instead of polling)
   - Better loading states
   - Error boundaries in React
   - Responsive design improvements
   - Accessibility improvements
   - Keyboard shortcuts

8. **Agent Improvements**
   - Multi-step reasoning for complex tickets
   - Confidence scores for categorizations
   - Batch processing optimization
   - Support for multiple LLM providers

### Low Priority

9. **Features**
   - Ticket editing/deletion
   - Export analysis results (CSV, PDF)
   - Ticket search and filtering
   - User preferences
   - Dark/light theme toggle

10. **DevOps**
    - CI/CD pipeline
    - Automated testing in CI
    - Staging environment
    - Blue-green deployments

11. **Documentation**
    - API versioning
    - OpenAPI spec enhancements
    - Architecture decision records (ADRs)
    - Developer onboarding guide


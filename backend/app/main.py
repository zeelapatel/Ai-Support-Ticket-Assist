"""
FastAPI application entry point
"""
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app import database
from app.database import get_db
from app import crud, schemas
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting up FastAPI application...")
    try:
        database.create_tables()
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.warning(f"Could not create database tables: {e}")
        logger.warning("Make sure PostgreSQL is running and DATABASE_URL is configured correctly")
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application...")
# Create FastAPI app
app = FastAPI(
    title="AI Support Ticket Assist",
    description="Backend API for AI-powered support ticket analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Support Ticket Assist API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ==================== API ENDPOINTS ====================

@app.post("/api/tickets", response_model=schemas.TicketsCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_tickets(
    request: schemas.TicketsCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create multiple tickets.
    
    Body: array of { title: string; description: string }
    Returns: inserted tickets
    """
    try:
        tickets_data = [{"title": t.title, "description": t.description} for t in request.tickets]
        created_tickets = crud.create_tickets(db, tickets_data)
        logger.info(f"Created {len(created_tickets)} tickets")
        return schemas.TicketsCreateResponse(
            tickets=[schemas.TicketResponse.model_validate(ticket) for ticket in created_tickets]
        )
    except Exception as e:
        logger.error(f"Error creating tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tickets: {str(e)}"
        )


@app.get("/api/tickets", response_model=List[schemas.TicketResponse])
async def get_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all tickets with pagination.
    """
    try:
        tickets = crud.get_tickets(db, skip=skip, limit=limit)
        return [schemas.TicketResponse.model_validate(ticket) for ticket in tickets]
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tickets: {str(e)}"
        )


@app.get("/api/tickets/{ticket_id}", response_model=schemas.TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific ticket by ID.
    """
    try:
        ticket = crud.get_ticket(db, ticket_id=ticket_id)
        if ticket is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with ID {ticket_id} not found"
            )
        return schemas.TicketResponse.model_validate(ticket)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch ticket: {str(e)}"
        )


@app.post("/api/analyze", response_model=schemas.AnalyzeResponse, status_code=status.HTTP_201_CREATED)
async def analyze_tickets(
    request: schemas.AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze tickets using LangGraph agent.
    
    Body: (optional) { ticketIds: number[] }
    - If ticketIds provided, analyze only those tickets
    - Otherwise, analyze all tickets
    
    Creates an analysis_runs row and corresponding ticket_analysis rows.
    Returns the created analysis_run and per-ticket analysis.
    """
    try:
        # Determine which tickets to analyze
        if request.ticket_ids:
            tickets = crud.get_tickets_by_ids(db, request.ticket_ids)
            if len(tickets) != len(request.ticket_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Some ticket IDs were not found"
                )
        else:
            tickets = crud.get_tickets(db, skip=0, limit=1000)  # Get all tickets
        
        if not tickets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No tickets found to analyze"
            )
        
        logger.info(f"Starting analysis for {len(tickets)} tickets")
        
        # Create analysis run
        analysis_run = crud.create_analysis_run(db, summary=None)
        
        # Call LangGraph agent here to analyze tickets
        
        analyses_data = []
        for ticket in tickets:
            analyses_data.append({
                "analysis_run_id": analysis_run.id,
                "ticket_id": ticket.id,
                "category": None,  # Will be set by agent
                "priority": None,  # Will be set by agent
                "notes": None      # Will be set by agent
            })
        
        # Create ticket analyses
        ticket_analyses = crud.create_ticket_analyses(db, analyses_data)
        
        # Update analysis run with summary (will be set by agent)
        # analysis_run.summary = analysis_results["summary"]
        # db.commit()
        # db.refresh(analysis_run)
        
        logger.info(f"Analysis run {analysis_run.id} created with {len(ticket_analyses)} analyses")
        
        return schemas.AnalyzeResponse(
            analysis_run=schemas.AnalysisRunResponse.model_validate(analysis_run),
            ticket_analyses=[schemas.TicketAnalysisResponse.model_validate(ta) for ta in ticket_analyses]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze tickets: {str(e)}"
        )


@app.get("/api/analysis/latest", response_model=schemas.LatestAnalysisResponse)
async def get_latest_analysis(db: Session = Depends(get_db)):
    """
    Get the latest analysis run with all ticket analyses and their associated tickets.
    """
    try:
        result = crud.get_latest_analysis_with_tickets(db)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No analysis runs found"
            )
        
        # Build response with ticket data included
        ticket_analyses_response = []
        for ta in result["ticket_analyses"]:
            ta_dict = {
                "id": ta.id,
                "analysis_run_id": ta.analysis_run_id,
                "ticket_id": ta.ticket_id,
                "category": ta.category,
                "priority": ta.priority,
                "notes": ta.notes,
                "ticket": schemas.TicketResponse.model_validate(ta.ticket) if ta.ticket else None
            }
            ticket_analyses_response.append(schemas.TicketAnalysisResponse(**ta_dict))
        
        return schemas.LatestAnalysisResponse(
            analysis_run=schemas.AnalysisRunResponse.model_validate(result["analysis_run"]),
            ticket_analyses=ticket_analyses_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch latest analysis: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )


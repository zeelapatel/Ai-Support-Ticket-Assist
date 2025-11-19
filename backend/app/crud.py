"""
Database CRUD operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import Ticket, AnalysisRun, TicketAnalysis


# ==================== TICKET OPERATIONS ====================

def create_tickets(db: Session, tickets_data: List[dict]) -> List[Ticket]:
    """
    Create multiple tickets in bulk.
    
    Args:
        db: Database session
        tickets_data: List of dicts with 'title' and 'description' keys
        
    Returns:
        List of created Ticket objects
    """
    tickets = [
        Ticket(title=ticket["title"], description=ticket["description"])
        for ticket in tickets_data
    ]
    db.add_all(tickets)
    db.commit()
    for ticket in tickets:
        db.refresh(ticket)
    return tickets


def get_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
    """
    Get all tickets with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Ticket objects
    """
    return db.query(Ticket).offset(skip).limit(limit).all()


def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
    """
    Get a single ticket by ID.
    
    Args:
        db: Database session
        ticket_id: ID of the ticket
        
    Returns:
        Ticket object or None if not found
    """
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_tickets_by_ids(db: Session, ticket_ids: List[int]) -> List[Ticket]:
    """
    Get multiple tickets by their IDs.
    
    Args:
        db: Database session
        ticket_ids: List of ticket IDs
        
    Returns:
        List of Ticket objects
    """
    return db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).all()


# ==================== ANALYSIS RUN OPERATIONS ====================

def create_analysis_run(db: Session, summary: Optional[str] = None) -> AnalysisRun:
    """
    Create a new analysis run.
    
    Args:
        db: Database session
        summary: Optional summary text
        
    Returns:
        Created AnalysisRun object
    """
    analysis_run = AnalysisRun(summary=summary)
    db.add(analysis_run)
    db.commit()
    db.refresh(analysis_run)
    return analysis_run


def get_analysis_run(db: Session, run_id: int) -> Optional[AnalysisRun]:
    """
    Get an analysis run by ID.
    
    Args:
        db: Database session
        run_id: ID of the analysis run
        
    Returns:
        AnalysisRun object or None if not found
    """
    return db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()


def get_latest_analysis_run(db: Session) -> Optional[AnalysisRun]:
    """
    Get the most recent analysis run.
    
    Args:
        db: Database session
        
    Returns:
        Latest AnalysisRun object or None if no runs exist
    """
    return db.query(AnalysisRun).order_by(desc(AnalysisRun.created_at)).first()


def update_analysis_run_summary(db: Session, run_id: int, summary: str) -> Optional[AnalysisRun]:
    """
    Update the summary of an analysis run.
    
    Args:
        db: Database session
        run_id: ID of the analysis run
        summary: Summary text to set
        
    Returns:
        Updated AnalysisRun object or None if not found
    """
    analysis_run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if analysis_run:
        analysis_run.summary = summary
        db.commit()
        db.refresh(analysis_run)
    return analysis_run


# ==================== TICKET ANALYSIS OPERATIONS ====================

def create_ticket_analyses(
    db: Session, 
    analyses_data: List[dict]
) -> List[TicketAnalysis]:
    """
    Create multiple ticket analyses in bulk.
    
    Args:
        db: Database session
        analyses_data: List of dicts with keys:
            - analysis_run_id: int
            - ticket_id: int
            - category: str
            - priority: str
            - notes: Optional[str]
            
    Returns:
        List of created TicketAnalysis objects
    """
    analyses = [
        TicketAnalysis(
            analysis_run_id=analysis["analysis_run_id"],
            ticket_id=analysis["ticket_id"],
            category=analysis.get("category"),
            priority=analysis.get("priority"),
            notes=analysis.get("notes")
        )
        for analysis in analyses_data
    ]
    db.add_all(analyses)
    db.commit()
    for analysis in analyses:
        db.refresh(analysis)
    return analyses


def get_ticket_analyses_by_run_id(
    db: Session, 
    run_id: int
) -> List[TicketAnalysis]:
    """
    Get all ticket analyses for a specific analysis run.
    
    Args:
        db: Database session
        run_id: ID of the analysis run
        
    Returns:
        List of TicketAnalysis objects
    """
    return (
        db.query(TicketAnalysis)
        .filter(TicketAnalysis.analysis_run_id == run_id)
        .all()
    )


def get_all_analysis_runs(db: Session, skip: int = 0, limit: int = 100) -> List[AnalysisRun]:
    """
    Get all analysis runs with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of AnalysisRun objects ordered by created_at (newest first)
    """
    return (
        db.query(AnalysisRun)
        .order_by(desc(AnalysisRun.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_analysis_run_with_tickets(db: Session, run_id: int) -> Optional[dict]:
    """
    Get a specific analysis run with all ticket analyses and their associated tickets.
    
    Args:
        db: Database session
        run_id: ID of the analysis run
        
    Returns:
        Dictionary with:
            - analysis_run: AnalysisRun object
            - ticket_analyses: List of TicketAnalysis objects with loaded ticket relationships
        Returns None if analysis run not found
    """
    analysis_run = get_analysis_run(db, run_id)
    if not analysis_run:
        return None
    
    # Get ticket analyses with eager loading of ticket relationship
    ticket_analyses = (
        db.query(TicketAnalysis)
        .filter(TicketAnalysis.analysis_run_id == run_id)
        .all()
    )
    
    return {
        "analysis_run": analysis_run,
        "ticket_analyses": ticket_analyses
    }


def get_latest_analysis_with_tickets(db: Session) -> Optional[dict]:
    """
    Get the latest analysis run with all ticket analyses and their associated tickets.
    This is used for the GET /api/analysis/latest endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with:
            - analysis_run: AnalysisRun object
            - ticket_analyses: List of TicketAnalysis objects with loaded ticket relationships
        Returns None if no analysis runs exist
    """
    analysis_run = get_latest_analysis_run(db)
    if not analysis_run:
        return None
    
    # Get ticket analyses with eager loading of ticket relationship
    ticket_analyses = (
        db.query(TicketAnalysis)
        .filter(TicketAnalysis.analysis_run_id == analysis_run.id)
        .all()
    )
    
    return {
        "analysis_run": analysis_run,
        "ticket_analyses": ticket_analyses
    }


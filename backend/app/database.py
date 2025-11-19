"""
Database connection and configuration
"""
import os
from typing import Generator
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/support_tickets"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship to ticket analysis
    analyses = relationship("TicketAnalysis", back_populates="ticket")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    summary = Column(Text)
    
    # Relationship to ticket analyses
    ticket_analyses = relationship("TicketAnalysis", back_populates="analysis_run")

class TicketAnalysis(Base):
    __tablename__ = "ticket_analysis"

    id = Column(Integer, primary_key=True, index=True)
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id"))
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    category = Column(Text)
    priority = Column(Text)
    notes = Column(Text)
    
    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="ticket_analyses")
    ticket = relationship("Ticket", back_populates="analyses")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

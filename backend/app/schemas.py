"""
Pydantic schemas for request/response validation
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# ==================== TICKET SCHEMAS ====================

class TicketBase(BaseModel):
    title: str
    description: str


class TicketCreate(TicketBase):
    pass


class TicketResponse(TicketBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TicketsCreateRequest(BaseModel):
    tickets: List[TicketCreate]


class TicketsCreateResponse(BaseModel):
    tickets: List[TicketResponse]


# ==================== ANALYSIS RUN SCHEMAS ====================

class AnalysisRunBase(BaseModel):
    summary: Optional[str] = None


class AnalysisRunResponse(BaseModel):
    id: int
    created_at: datetime
    summary: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== TICKET ANALYSIS SCHEMAS ====================

class TicketAnalysisBase(BaseModel):
    category: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None


class TicketAnalysisCreate(TicketAnalysisBase):
    analysis_run_id: int
    ticket_id: int


class TicketAnalysisResponse(TicketAnalysisBase):
    id: int
    analysis_run_id: int
    ticket_id: int
    ticket: Optional[TicketResponse] = None
    
    class Config:
        from_attributes = True


# ==================== ANALYSIS REQUEST/RESPONSE SCHEMAS ====================

class AnalyzeRequest(BaseModel):
    ticket_ids: Optional[List[int]] = None


class AnalyzeResponse(BaseModel):
    analysis_run: AnalysisRunResponse
    ticket_analyses: List[TicketAnalysisResponse]


class LatestAnalysisResponse(BaseModel):
    analysis_run: AnalysisRunResponse
    ticket_analyses: List[TicketAnalysisResponse]


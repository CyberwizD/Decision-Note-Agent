"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ===== Request Models (Incoming from Telex) =====

class A2ARequest(BaseModel):
    """
    Standard A2A protocol request from Telex
    """
    user: str
    message: str
    channel_id: Optional[str] = None
    message_id: Optional[str] = None


class VoteRequest(BaseModel):
    """
    Vote on a proposed decision
    """
    user: str
    proposal_id: int
    vote: str  # "approve" or "reject"


# ===== Response Models (Outgoing to Telex) =====

class A2AResponse(BaseModel):
    """
    Standard response to Telex
    """
    type: str = "text"  # text, markdown, error
    content: str


# ===== Internal Models =====

class Decision(BaseModel):
    """
    Decision model
    """
    id: Optional[int] = None
    text: str
    original_text: Optional[str] = None
    user: str
    last_edited_by: Optional[str] = None
    last_edited_at: Optional[datetime] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    edit_count: int = 0
    topic: Optional[str] = None
    metadata: Optional[str] = None


class ProposedDecision(BaseModel):
    """
    Proposed decision pending approval
    """
    id: Optional[int] = None
    text: str
    proposer: str
    timestamp: datetime = Field(default_factory=datetime.now)
    approvals: List[str] = Field(default_factory=list)
    rejections: List[str] = Field(default_factory=list)
    status: str = "pending"  # pending, approved, rejected, expired
    threshold: int = 2
    expires_at: Optional[datetime] = None


class DecisionHistory(BaseModel):
    """
    Edit history for a decision
    """
    id: Optional[int] = None
    decision_id: int
    text: str
    edited_by: str
    edited_at: datetime = Field(default_factory=datetime.now)


class ValidationResult(BaseModel):
    """
    Result from Gemini validation
    """
    is_valid: bool
    reason: str
    confidence: Optional[float] = None


class DailySummary(BaseModel):
    """
    Daily summary structure
    """
    date: str
    total_decisions: int
    decisions: List[Decision]
    ai_summary: str
    themes: Optional[List[str]] = None
    
"""
Voting/approval service for proposed decisions
"""
from app.database import execute_query, execute_insert
from app.models import ProposedDecision, Decision
from app.config import get_settings
from typing import Optional
from datetime import datetime, timedelta
import json

settings = get_settings()


class VotingService:
    """
    Service for managing proposed decisions and voting
    """
    
    @staticmethod
    async def create_proposal(text: str, proposer: str) -> ProposedDecision:
        """
        Create a new decision proposal
        """
        expires_at = datetime.now() + timedelta(minutes=settings.voting_timeout_minutes)
        
        query = """
        INSERT INTO proposed_decisions 
        (text, proposer, threshold, expires_at, approvals, rejections)
        VALUES (?, ?, ?, ?, '[]', '[]')
        """
        
        proposal_id = await execute_insert(
            query, 
            (text, proposer, settings.voting_approval_threshold, expires_at.isoformat())
        )
        
        return ProposedDecision(
            id=proposal_id,
            text=text,
            proposer=proposer,
            threshold=settings.voting_approval_threshold,
            expires_at=expires_at
        )
    
    @staticmethod
    async def get_proposal_by_id(proposal_id: int) -> Optional[ProposedDecision]:
        """
        Get a proposal by ID
        """
        query = "SELECT * FROM proposed_decisions WHERE id = ?"
        result = await execute_query(query, (proposal_id,), fetch_one=True)
        
        if not result:
            return None
        
        return ProposedDecision(
            id=result['id'],
            text=result['text'],
            proposer=result['proposer'],
            timestamp=datetime.fromisoformat(result['timestamp']),
            approvals=json.loads(result['approvals']),
            rejections=json.loads(result['rejections']),
            status=result['status'],
            threshold=result['threshold'],
            expires_at=datetime.fromisoformat(result['expires_at']) if result['expires_at'] else None
        )
    
    @staticmethod
    async def add_vote(proposal_id: int, user: str, vote_type: str) -> Optional[ProposedDecision]:
        """
        Add a vote (approve/reject) to a proposal
        
        Args:
            proposal_id: ID of the proposal
            user: Username voting
            vote_type: "approve" or "reject"
            
        Returns:
            Updated ProposedDecision or None if proposal not found
        """
        proposal = await VotingService.get_proposal_by_id(proposal_id)
        
        if not proposal:
            return None
        
        # Check if proposal is still pending
        if proposal.status != "pending":
            return proposal
        
        # Check if expired
        if proposal.expires_at and datetime.now() > proposal.expires_at:
            await VotingService._mark_expired(proposal_id)
            proposal.status = "expired"
            return proposal
        
        # Check if user is proposer and self-approval not allowed
        if not settings.allow_self_approve and user == proposal.proposer:
            return None  # Silent fail or could return error
        
        # Remove user from opposite list if present
        if vote_type == "approve":
            if user in proposal.rejections:
                proposal.rejections.remove(user)
            if user not in proposal.approvals:
                proposal.approvals.append(user)
        else:  # reject
            if user in proposal.approvals:
                proposal.approvals.remove(user)
            if user not in proposal.rejections:
                proposal.rejections.append(user)
        
        # Update database
        update_query = """
        UPDATE proposed_decisions 
        SET approvals = ?, rejections = ?
        WHERE id = ?
        """
        
        await execute_query(
            update_query,
            (json.dumps(proposal.approvals), json.dumps(proposal.rejections), proposal_id)
        )
        
        # Check if threshold met
        if len(proposal.approvals) >= proposal.threshold:
            await VotingService._mark_approved(proposal_id)
            proposal.status = "approved"
        elif len(proposal.rejections) >= proposal.threshold:
            await VotingService._mark_rejected(proposal_id)
            proposal.status = "rejected"
        
        return proposal
    
    @staticmethod
    async def _mark_approved(proposal_id: int):
        """
        Mark proposal as approved
        """
        query = "UPDATE proposed_decisions SET status = 'approved' WHERE id = ?"
        await execute_query(query, (proposal_id,))
    
    @staticmethod
    async def _mark_rejected(proposal_id: int):
        """
        Mark proposal as rejected
        """
        query = "UPDATE proposed_decisions SET status = 'rejected' WHERE id = ?"
        await execute_query(query, (proposal_id,))
    
    @staticmethod
    async def _mark_expired(proposal_id: int):
        """
        Mark proposal as expired
        """
        query = "UPDATE proposed_decisions SET status = 'expired' WHERE id = ?"
        await execute_query(query, (proposal_id,))
    
    @staticmethod
    async def convert_proposal_to_decision(proposal: ProposedDecision) -> Decision:
        """
        Convert approved proposal to a decision
        """
        from services.decision_service import DecisionService
        
        decision = await DecisionService.add_decision(
            text=proposal.text,
            user=proposal.proposer,
            topic=None
        )
        
        return decision
    
    @staticmethod
    async def get_pending_proposals() -> list[ProposedDecision]:
        """
        Get all pending proposals
        """
        query = """
        SELECT * FROM proposed_decisions 
        WHERE status = 'pending'
        ORDER BY timestamp DESC
        """
        results = await execute_query(query)
        
        proposals = []
        for row in results:
            proposal = ProposedDecision(
                id=row['id'],
                text=row['text'],
                proposer=row['proposer'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                approvals=json.loads(row['approvals']),
                rejections=json.loads(row['rejections']),
                status=row['status'],
                threshold=row['threshold'],
                expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None
            )
            
            # Check expiration
            if proposal.expires_at and datetime.now() > proposal.expires_at:
                await VotingService._mark_expired(proposal.id)
            else:
                proposals.append(proposal)
        
        return proposals
    
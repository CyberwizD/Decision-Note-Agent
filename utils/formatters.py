"""
Response formatting utilities
"""
from app.models import Decision, ProposedDecision
from typing import List
from datetime import datetime


class ResponseFormatter:
    """
    Format responses for Telex display
    """
    
    @staticmethod
    def format_decision_added(decision: Decision) -> str:
        """
        Format success message when decision is added
        """
        return (
            f"✅ Decision recorded: \"{decision.text}\"\n"
            f"   (added by {decision.user} on {decision.timestamp.strftime('%b %d, %Y at %I:%M %p')})"
        )
    
    @staticmethod
    def format_decision_list(decisions: List[Decision]) -> str:
        """
        Format list of decisions
        """
        if not decisions:
            return "📋 No decisions recorded yet. Start logging with `add \"Your decision\"`"
        
        header = f"🗂 Recorded Decisions ({len(decisions)}):\n\n"
        
        items = []
        for i, d in enumerate(decisions, 1):
            date_str = d.timestamp.strftime("%b %d")
            edit_note = f" (edited)" if d.edit_count > 0 else ""
            items.append(f"{i}. [{date_str}] {d.text}{edit_note}\n   by {d.user}")
        
        return header + "\n".join(items)
    
    @staticmethod
    def format_decision_updated(decision: Decision, editor: str) -> str:
        """
        Format message when decision is updated
        """
        return (
            f"✅ Decision #{decision.id} updated: \"{decision.text}\"\n"
            f"   (originally: \"{decision.original_text}\" by {decision.user})\n"
            f"   (edited by {editor} on {datetime.now().strftime('%b %d, %Y at %I:%M %p')})"
        )
    
    @staticmethod
    def format_search_results(decisions: List[Decision], query: str) -> str:
        """
        Format search results
        """
        if not decisions:
            return f"🔍 No decisions found matching \"{query}\""
        
        header = f"🔍 Found {len(decisions)} decision(s) matching \"{query}\":\n\n"
        
        items = []
        for i, d in enumerate(decisions, 1):
            date_str = d.timestamp.strftime("%b %d")
            items.append(f"{i}. [{date_str}] {d.text}\n   by {d.user}")
        
        return header + "\n".join(items)
    
    @staticmethod
    def format_proposal_created(proposal: ProposedDecision) -> str:
        """
        Format message when decision is proposed
        """
        return (
            f"📋 Decision Proposed: \"{proposal.text}\"\n"
            f"   (proposed by {proposal.proposer})\n\n"
            f"React with:\n"
            f"• `approve {proposal.id}` to approve\n"
            f"• `reject {proposal.id}` to reject\n\n"
            f"Need {proposal.threshold} approvals to log.\n"
            f"Current: ✅ ({len(proposal.approvals)}) | ❌ ({len(proposal.rejections)})"
        )
    
    @staticmethod
    def format_vote_update(proposal: ProposedDecision) -> str:
        """
        Format vote status update
        """
        return (
            f"📊 Proposal #{proposal.id} status:\n"
            f"\"{proposal.text}\"\n\n"
            f"✅ Approvals: {len(proposal.approvals)} (need {proposal.threshold})\n"
            f"❌ Rejections: {len(proposal.rejections)}\n\n"
            f"Approved by: {', '.join(proposal.approvals) if proposal.approvals else 'None yet'}\n"
            f"Rejected by: {', '.join(proposal.rejections) if proposal.rejections else 'None yet'}"
        )
    
    @staticmethod
    def format_proposal_approved(proposal: ProposedDecision) -> str:
        """
        Format message when proposal is approved
        """
        return (
            f"🎉 Decision Approved & Logged!\n"
            f"\"{proposal.text}\"\n\n"
            f"Proposed by: {proposal.proposer}\n"
            f"Approved by: {', '.join(proposal.approvals)}"
        )
    
    @staticmethod
    def format_proposal_rejected(proposal: ProposedDecision) -> str:
        """
        Format message when proposal is rejected
        """
        return (
            f"❌ Proposal Rejected\n"
            f"\"{proposal.text}\"\n\n"
            f"This decision was not logged to the registry."
        )
    
    @staticmethod
    def format_error(message: str) -> str:
        """
        Format error message
        """
        return f"⚠️ {message}"
    
    @staticmethod
    def format_help() -> str:
        """
        Format help message with available commands
        """
        return """
📖 **DecisionNote Commands**

**Direct Commands:**
• `add "Your decision"` - Log a decision immediately
• `list` - View all recorded decisions
• `search "keyword"` - Search decisions by keyword
• `edit <id> "New text"` - Update an existing decision
• `history <id>` - View edit history of a decision
• `help` - Show this help message

**Voting/Approval:**
• `propose "Your decision"` - Propose a decision for team approval
• `approve <id>` - Approve a proposed decision
• `reject <id>` - Reject a proposed decision

**Examples:**
`add "Use PostgreSQL for the database"`
`propose "Switch to React for frontend"`
`search "backend"`
`edit 5 "Use MongoDB instead"`
`approve 3`

**Daily Summary:**
Automatically posted every day with AI-generated insights!
        """.strip()

"""
Main A2A endpoint for handling Telex commands
"""
from fastapi import APIRouter, HTTPException
from app.models import A2ARequest, A2AResponse
from services.decision_service import DecisionService
from services.voting_service import VotingService
from services.gemini_service import validate_decision
from utils.parsers import CommandParser
from utils.formatters import ResponseFormatter

router = APIRouter()


@router.post("/a2a", response_model=A2AResponse)
async def handle_a2a_request(request: A2ARequest):
    """
    Main A2A endpoint - handles all commands from Telex
    """
    user = request.user
    message = request.message.strip()
    
    # Parse command
    command, argument = CommandParser.parse_command(message)
    
    try:
        # ===== ADD DECISION (Direct) =====
        if command == "add":
            decision_text = CommandParser.extract_decision_text(message)
            
            if not decision_text:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        "Please provide decision text. Example: `/decision add \"Use MongoDB\"`"
                    )
                )
            
            # Validate with Gemini
            validation = await validate_decision(decision_text)
            
            if not validation.is_valid:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        f"Invalid decision: {validation.reason}\n\n"
                    f"Please provide a clear, meaningful decision statement."
                    )
                )
            
            # Add decision
            decision = await DecisionService.add_decision(decision_text, user)
            
            return A2AResponse(
                type="text",
                content=ResponseFormatter.format_decision_added(decision)
            )
        
        # ===== PROPOSE DECISION (For voting) =====
        elif command == "propose":
            decision_text = CommandParser.extract_decision_text(message)
            
            if not decision_text:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        "Please provide decision text. Example: `/decision propose \"Switch to React\"`"
                    )
                )
            
            # Validate with Gemini
            validation = await validate_decision(decision_text)
            
            if not validation.is_valid:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        f"Invalid decision: {validation.reason}"
                    )
                )
            
            # Create proposal
            proposal = await VotingService.create_proposal(decision_text, user)
            
            return A2AResponse(
                type="text",
                content=ResponseFormatter.format_proposal_created(proposal)
            )
        
        # ===== APPROVE PROPOSAL =====
        elif command == "approve":
            proposal_id, _ = CommandParser.parse_vote_command(message)
            
            if not proposal_id:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        "Please specify proposal ID. Example: `/decision approve 3`"
                    )
                )
            
            proposal = await VotingService.add_vote(proposal_id, user, "approve")
            
            if not proposal:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        f"Proposal #{proposal_id} not found or you cannot vote on your own proposal."
                    )
                )
            
            # Check if approved
            if proposal.status == "approved":
                # Convert to decision
                decision = await VotingService.convert_proposal_to_decision(proposal)
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_proposal_approved(proposal)
                )
            elif proposal.status == "expired":
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error("This proposal has expired.")
                )
            else:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_vote_update(proposal)
                )
        
        # ===== REJECT PROPOSAL =====
        elif command == "reject":
            proposal_id, _ = CommandParser.parse_vote_command(message)
            
            if not proposal_id:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        "Please specify proposal ID. Example: `/decision reject 3`"
                    )
                )
            
            proposal = await VotingService.add_vote(proposal_id, user, "reject")
            
            if not proposal:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(f"Proposal #{proposal_id} not found.")
                )
            
            # Check if rejected
            if proposal.status == "rejected":
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_proposal_rejected(proposal)
                )
            else:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_vote_update(proposal)
                )
        
        # ===== LIST DECISIONS =====
        elif command == "list":
            decisions = await DecisionService.get_all_decisions(limit=20)
            
            return A2AResponse(
                type="text",
                content=ResponseFormatter.format_decision_list(decisions)
            )
        
        # ===== SEARCH DECISIONS =====
        elif command == "search":
            query = CommandParser.parse_search_query(message)
            
            if not query:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        "Please provide search query. Example: `/decision search backend`"
                    )
                )
            
            decisions = await DecisionService.search_decisions(query)
            
            return A2AResponse(
                type="text",
                content=ResponseFormatter.format_search_results(decisions, query)
            )
        
        # ===== EDIT DECISION =====
        elif command == "edit":
            decision_id, new_text = CommandParser.parse_edit_command(message)
            
            if not decision_id or not new_text:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        "Please provide decision ID and new text.\n"
                        "Example: `/decision edit 5 \"Use PostgreSQL instead\"`"
                    )
                )
            
            # Validate new text
            validation = await validate_decision(new_text)
            
            if not validation.is_valid:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        f"Invalid decision text: {validation.reason}"
                    )
                )
            
            decision = await DecisionService.update_decision(decision_id, new_text, user)
            
            if not decision:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(f"Decision #{decision_id} not found.")
                )
            
            return A2AResponse(
                type="text",
                content=ResponseFormatter.format_decision_updated(decision, user)
            )
        
        # ===== HISTORY =====
        elif command == "history":
            try:
                decision_id = int(argument) if argument else None
            except ValueError:
                decision_id = None
            
            if not decision_id:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(
                        "Please provide decision ID. Example: `/decision history 5`"
                    )
                )
            
            decision = await DecisionService.get_decision_by_id(decision_id)
            
            if not decision:
                return A2AResponse(
                    type="text",
                    content=ResponseFormatter.format_error(f"Decision #{decision_id} not found.")
                )
            
            history = await DecisionService.get_decision_history(decision_id)
            
            if not history:
                return A2AResponse(
                    type="text",
                    content=f"📜 Decision #{decision_id} History:\n\nNo edits yet. Original text:\n\"{decision.original_text}\" (by {decision.user})"
                )
            
            history_text = f"📜 Decision #{decision_id} History:\n\n"
            history_text += f"Current: \"{decision.text}\"\n\n"
            history_text += "Previous versions:\n"
            
            for i, h in enumerate(history, 1):
                history_text += f"{i}. \"{h.text}\" (edited by {h.edited_by} on {h.edited_at.strftime('%b %d, %I:%M %p')})\n"
            
            return A2AResponse(
                type="text",
                content=history_text
            )
        
        # ===== HELP =====
        elif command == "help" or command == "unknown":
            return A2AResponse(
                type="text",
                content=ResponseFormatter.format_help()
            )
        
        # ===== UNKNOWN COMMAND =====
        else:
            return A2AResponse(
                type="text",
                content=ResponseFormatter.format_error(
                    f"Unknown command: '{command}'. Type `/decision help` for available commands."
                )
            )
    
    except Exception as e:
        print(f"❌ Error handling command: {e}")
        return A2AResponse(
            type="text",
            content=ResponseFormatter.format_error(
                "An error occurred while processing your request. Please try again."
            )
        )
    
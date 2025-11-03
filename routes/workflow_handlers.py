"""
Handlers for specific A2A methods and commands.
"""
from app.models import MessageParams, TaskResult, TaskStatus, A2AMessage, MessagePart, Artifact, ExecuteParams
from services.decision_service import DecisionService
from services.voting_service import VotingService
from services.gemini_service import validate_decision
from utils.parsers import CommandParser
from utils.formatters import ResponseFormatter
from uuid import uuid4

async def process_user_message(user_message: A2AMessage) -> TaskResult:
    """
    Processes a single user message and returns a TaskResult.
    """
    message_text = ""
    # The user's command is now in the `data` part of the message
    if len(user_message.parts) > 1 and user_message.parts[1].kind == "data":
        # The actual command is the last text part in the data array
        message_text = user_message.parts[1].data[-1]['text'].strip()
    else:
        for part in user_message.parts:
            if part.kind == "text":
                message_text = part.text.strip()
                break

    command, _ = CommandParser.parse_command(message_text)
    
    handler = COMMAND_HANDLERS.get(command, handle_unknown_command)
    # Pass the extracted message_text to the handler
    return await handler(user_message, message_text)

async def handle_message_send(params: MessageParams) -> TaskResult:
    """
    Handles the 'message/send' method.
    """
    return await process_user_message(params.message)

async def handle_execute(params: ExecuteParams) -> TaskResult:
    """
    Handles the 'execute' method by processing the last message in the history.
    """
    if not params.messages:
        # Create a generic error response if there are no messages
        return TaskResult(
            id=params.taskId or str(uuid4()),
            contextId=params.contextId or str(uuid4()),
            status=TaskStatus(
                state="failed",
                message=A2AMessage(
                    role="agent",
                    parts=[MessagePart(kind="text", text="Cannot execute with an empty message history.")]
                )
            )
        )
    
    last_user_message = params.messages[-1]
    return await process_user_message(last_user_message)

async def handle_add_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    decision_text = CommandParser.extract_decision_text(message_text)
    
    if not decision_text:
        return create_error_response(user_message, "Please provide decision text.")

    user = (user_message.metadata or {}).get("user", "unknown")
    decision = await DecisionService.add_decision(decision_text, user)
    response_text = ResponseFormatter.format_decision_added(decision)
    return create_success_response(user_message, response_text)

async def handle_list_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    decisions = await DecisionService.get_all_decisions(limit=20)
    response_text = ResponseFormatter.format_decision_list(decisions)
    return create_success_response(user_message, response_text)

async def handle_search_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    query = CommandParser.parse_search_query(message_text)
    if not query:
        return create_error_response(user_message, "Please provide a search query.")
    decisions = await DecisionService.search_decisions(query)
    response_text = ResponseFormatter.format_search_results(decisions, query)
    return create_success_response(user_message, response_text)

async def handle_edit_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    decision_id, new_text = CommandParser.parse_edit_command(message_text)
    if not decision_id or not new_text:
        return create_error_response(user_message, "Invalid edit command format.")
    user = (user_message.metadata or {}).get("user", "unknown")
    decision = await DecisionService.update_decision(decision_id, new_text, user)
    if not decision:
        return create_error_response(user_message, f"Decision #{decision_id} not found.")
    response_text = ResponseFormatter.format_decision_updated(decision, user)
    return create_success_response(user_message, response_text)

async def handle_history_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    _, argument = CommandParser.parse_command(message_text)
    try:
        decision_id = int(argument)
    except (ValueError, TypeError):
        return create_error_response(user_message, "Invalid decision ID.")
    history = await DecisionService.get_decision_history(decision_id)
    # This needs a proper formatter in a real implementation
    response_text = f"History for decision #{decision_id}:\\n" + "\\n".join([f"- {h.text}" for h in history])
    return create_success_response(user_message, response_text)

async def handle_propose_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    decision_text = CommandParser.extract_decision_text(message_text)
    if not decision_text:
        return create_error_response(user_message, "Please provide proposal text.")
    user = (user_message.metadata or {}).get("user", "unknown")
    proposal = await VotingService.create_proposal(decision_text, user)
    response_text = ResponseFormatter.format_proposal_created(proposal)
    return create_success_response(user_message, response_text)

async def handle_approve_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    proposal_id, _ = CommandParser.parse_vote_command(message_text)
    if not proposal_id:
        return create_error_response(user_message, "Invalid approve command format.")
    user = (user_message.metadata or {}).get("user", "unknown")
    proposal = await VotingService.add_vote(proposal_id, user, "approve")
    if not proposal:
        return create_error_response(user_message, f"Proposal #{proposal_id} not found.")
    if proposal.status == "approved":
        response_text = ResponseFormatter.format_proposal_approved(proposal)
    else:
        response_text = ResponseFormatter.format_vote_update(proposal)
    return create_success_response(user_message, response_text)

async def handle_reject_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    proposal_id, _ = CommandParser.parse_vote_command(message_text)
    if not proposal_id:
        return create_error_response(user_message, "Invalid reject command format.")
    user = (user_message.metadata or {}).get("user", "unknown")
    proposal = await VotingService.add_vote(proposal_id, user, "reject")
    if not proposal:
        return create_error_response(user_message, f"Proposal #{proposal_id} not found.")
    if proposal.status == "rejected":
        response_text = ResponseFormatter.format_proposal_rejected(proposal)
    else:
        response_text = ResponseFormatter.format_vote_update(proposal)
    return create_success_response(user_message, response_text)

async def handle_help_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    response_text = ResponseFormatter.format_help()
    return create_success_response(user_message, response_text)

async def handle_unknown_command(user_message: A2AMessage, message_text: str) -> TaskResult:
    return create_error_response(user_message, "Unknown command. Type `help` for available commands.")

COMMAND_HANDLERS = {
    "add": handle_add_command,
    "list": handle_list_command,
    "search": handle_search_command,
    "edit": handle_edit_command,
    "history": handle_history_command,
    "propose": handle_propose_command,
    "approve": handle_approve_command,
    "reject": handle_reject_command,
    "help": handle_help_command,
}

# Helper functions to create responses
def create_success_response(user_message: A2AMessage, response_text: str, execution_results: dict = None, tool_results: dict = None) -> TaskResult:
    # Create the agent's response message, populating taskId and metadata from the user's message
    response_message = A2AMessage(
        role="agent",
        parts=[MessagePart(kind="text", text=response_text, data=None, file_url=None)],
        messageId=str(uuid4()), # Generate a new messageId for the agent's response
        taskId=user_message.taskId,
        contextId=user_message.contextId,
        metadata=user_message.metadata
    )
    
    artifacts = [
        Artifact(
            name="assistantResponse",
            parts=[MessagePart(kind="text", text=response_text, data=None, file_url=None)]
        )
    ]
    
    if execution_results:
        artifacts.append(Artifact(
            name="ExecutionResults",
            parts=[MessagePart(kind="data", data=execution_results, text=None, file_url=None)]
        ))
        
    if tool_results:
        artifacts.append(Artifact(
            name="ToolResults",
            parts=[MessagePart(kind="data", data=tool_results, text=None, file_url=None)]
        ))

    # Ensure user_message in history also has taskId and metadata if available
    user_message_for_history = user_message.model_copy(update={
        "taskId": user_message.taskId,
        "contextId": user_message.contextId,
        "metadata": user_message.metadata
    })

    return TaskResult(
        id=user_message.taskId or str(uuid4()),
        contextId=user_message.contextId or str(uuid4()),
        status=TaskStatus(state="completed", message=response_message),
        artifacts=artifacts,
        history=[user_message_for_history, response_message],
        kind="task" # Explicitly set kind to "task"
    )

def create_error_response(user_message: A2AMessage, error_text: str) -> TaskResult:
    error_message = A2AMessage(
        role="agent",
        parts=[MessagePart(kind="text", text=error_text)]
    )
    return TaskResult(
        id=user_message.taskId or str(uuid4()),
        contextId=user_message.contextId or str(uuid4()),
        status=TaskStatus(state="failed", message=error_message)
    )

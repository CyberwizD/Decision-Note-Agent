"""
Endpoint for serving the agent.json file for Telex discovery.
"""
from fastapi import APIRouter
from app.models import AgentCard, Provider, Capabilities, Skill, SkillExample

router = APIRouter()

@router.get("/.well-known/agent.json", response_model=AgentCard)
async def get_agent_card():
    """
    Returns the agent card, providing metadata about the agent's capabilities.
    """
    return AgentCard(
        name="Decision Note Agent",
        description="Transforms chat discussions into structured, searchable decision logs.",
        url="https://decision-note-agent-production.up.railway.app/a2a/agent/DecisionNote",
        provider=Provider(
            organization="Decision Note Inc.",
            url="https://decision-note-agent-production.up.railway.app"
        ),
        version="1.0.0",
        documentationUrl="https://decision-note-agent-production.up.railway.app/docs",
        capabilities=Capabilities(
            streaming=False,
            pushNotifications=True,  # For daily summaries
            stateTransitionHistory=False
        ),
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        skills=[
            Skill(
                id="add-decision",
                name="Add Decision",
                description="Adds a new decision to the log.",
                inputModes=["text/plain"],
                outputModes=["text/plain"],
                examples=[
                    SkillExample(
                        input={"parts": [{"text": "/decision add \"Use FastAPI for the new service\""}]},
                        output={"parts": [{"text": "Decision #1 added: \"Use FastAPI for the new service\""}]}
                    )
                ]
            ),
            Skill(
                id="list-decisions",
                name="List Decisions",
                description="Lists the most recent decisions.",
                inputModes=["text/plain"],
                outputModes=["text/plain"],
                examples=[
                    SkillExample(
                        input={"parts": [{"text": "/decision list"}]},
                        output={"parts": [{"text": "1. Use FastAPI..."}]}
                    )
                ]
            ),
            Skill(
                id="propose-decision",
                name="Propose Decision",
                description="Proposes a new decision for voting.",
                inputModes=["text/plain"],
                outputModes=["text/plain"],
                examples=[
                    SkillExample(
                        input={"parts": [{"text": "/decision propose \"Switch to React\""}]},
                        output={"parts": [{"text": "Proposal #1 created: \"Switch to React\""}]}
                    )
                ]
            ),
            Skill(
                id="approve-proposal",
                name="Approve Proposal",
                description="Approves a decision proposal.",
                inputModes=["text/plain"],
                outputModes=["text/plain"],
                examples=[
                    SkillExample(
                        input={"parts": [{"text": "/decision approve 1"}]},
                        output={"parts": [{"text": "Vote recorded for proposal #1."}]}
                    )
                ]
            ),
            Skill(
                id="reject-proposal",
                name="Reject Proposal",
                description="Rejects a decision proposal.",
                inputModes=["text/plain"],
                outputModes=["text/plain"],
                examples=[
                    SkillExample(
                        input={"parts": [{"text": "/decision reject 1"}]},
                        output={"parts": [{"text": "Vote recorded for proposal #1."}]}
                    )
                ]
            ),
            Skill(
                id="search-decisions",
                name="Search Decisions",
                description="Searches for decisions by keyword.",
                inputModes=["text/plain"],
                outputModes=["text/plain"],
                examples=[
                    SkillExample(
                        input={"parts": [{"text": "/decision search FastAPI"}]},
                        output={"parts": [{"text": "Found 1 decision matching 'FastAPI'..."}]}
                    )
                ]
            ),
            Skill(
                id="edit-decision",
                name="Edit Decision",
                description="Edits an existing decision.",
                inputModes=["text/plain"],
                outputModes=["text/plain"],
                examples=[
                    SkillExample(
                        input={"parts": [{"text": "/decision edit 1 \"Use FastAPI and Pydantic\""}]},
                        output={"parts": [{"text": "Decision #1 updated."}]}
                    )
                ]
            ),
            Skill(
                id="decision-history",
                name="Decision History",
                description="Shows the edit history of a decision.",
                inputModes=["text/plain"],
                outputModes=["text/plain"],
                examples=[
                    SkillExample(
                        input={"parts": [{"text": "/decision history 1"}]},
                        output={"parts": [{"text": "History for decision #1..."}]}
                    )
                ]
            ),
            Skill(
                id="help",
                name="Help",
                description="Shows a list of available commands.",
                inputModes=["text/plain"],
                outputModes=["text/plain"],
                examples=[
                    SkillExample(
                        input={"parts": [{"text": "/decision help"}]},
                        output={"parts": [{"text": "Available commands..."}]}
                    )
                ]
            )
        ]
    )

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
        url="https://decision-note-agent-production.up.railway.app/a2a",
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
            )
        ]
    )

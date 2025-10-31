"""
Scheduled trigger endpoints (for daily summaries, etc.)
"""
from fastapi import APIRouter
from app.models import A2AResponse
from services.summary_service import SummaryService

router = APIRouter()


@router.post("/trigger/daily-summary", response_model=A2AResponse)
async def trigger_daily_summary():
    """
    Endpoint to trigger daily summary
    This can be called by:
    - Telex automation scheduler
    - External cron job
    - Manual trigger for testing
    """
    try:
        summary = await SummaryService.generate_todays_summary()
        
        return A2AResponse(
            type="text",
            content=summary
        )
    
    except Exception as e:
        print(f"❌ Error generating daily summary: {e}")
        return A2AResponse(
            type="text",
            content="⚠️ Failed to generate daily summary. Please try again later."
        )


@router.get("/trigger/test-summary")
async def test_summary():
    """
    Test endpoint for development (returns JSON instead of A2A format)
    """
    summary = await SummaryService.generate_todays_summary()
    
    return {
        "success": True,
        "summary": summary
    }

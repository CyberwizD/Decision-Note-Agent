"""
Scheduled trigger endpoints for daily summaries and other events.
"""
from fastapi import APIRouter, Body
from app.models import TaskResult, TaskStatus, A2AMessage, MessagePart
from services.summary_service import SummaryService
from services.notification_service import send_webhook_notification
from uuid import uuid4

router = APIRouter()


@router.post("/trigger/daily-summary")
async def trigger_daily_summary(webhook_url: str = Body(..., embed=True)):
    """
    Endpoint to trigger the daily summary.
    This is designed to be called by a scheduler (e.g., a cron job or a Telex automation)
    and will send the summary to the provided webhook URL.
    """
    try:
        summary_text = await SummaryService.generate_todays_summary()
        
        # Create an A2A TaskResult with the summary
        summary_message = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=summary_text)]
        )
        task_result = TaskResult(
            id=str(uuid4()),
            contextId="daily-summary",
            status=TaskStatus(state="completed", message=summary_message)
        )
        
        # Send the summary to the webhook
        await send_webhook_notification(webhook_url, task_result)
        
        return {"status": "success", "message": "Daily summary sent to webhook."}
    
    except Exception as e:
        print(f"❌ Error generating daily summary: {e}")
        # In a real-world scenario, you might want to send an error notification
        # to the webhook as well, but for now, we'll just return an error.
        return {"status": "error", "message": "Failed to generate daily summary."}

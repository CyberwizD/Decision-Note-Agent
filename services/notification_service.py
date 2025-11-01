"""
Service for sending A2A notifications to a webhook.
"""
import httpx
from app.models import TaskResult

async def send_webhook_notification(webhook_url: str, result: TaskResult):
    """
    Sends a TaskResult to the specified webhook URL.
    """
    async with httpx.AsyncClient() as client:
        await client.post(
            webhook_url,
            json=result.model_dump(exclude_none=True),
            headers={"Content-Type": "application/json"}
        )

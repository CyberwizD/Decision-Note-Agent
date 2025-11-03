"""
Service for sending A2A notifications to a webhook.
"""
import httpx
from app.models import TaskResult

async def send_webhook_notification(webhook_url: str, result: TaskResult):
    """
    Sends a TaskResult to the specified webhook URL with a timeout and error handling.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=result.model_dump(exclude_none=True),
                headers={"Content-Type": "application/json"},
                timeout=10.0  # Set a 10-second timeout
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            print(f"✅ Successfully sent notification to {webhook_url}")
    except httpx.TimeoutException:
        print(f"❌ Timeout error sending notification to {webhook_url}")
    except httpx.RequestError as e:
        print(f"❌ Error sending notification to {webhook_url}: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

"""
Daily summary generation service
"""
from services.decision_service import DecisionService
from services.gemini_service import generate_daily_summary
# from app.models import DailySummary
from datetime import datetime


class SummaryService:
    """
    Service for generating daily summaries
    """
    
    @staticmethod
    async def generate_todays_summary() -> str:
        """
        Generate today's decision summary
        
        Returns:
            Formatted summary string ready to send to channel
        """
        # Get today's decisions
        decisions = await DecisionService.get_todays_decisions()
        
        # Get today's date
        today = datetime.now().strftime("%B %d, %Y")
        
        # Generate AI summary
        summary_text = await generate_daily_summary(decisions, today)
        
        return summary_text
    
    @staticmethod
    async def should_send_summary() -> bool:
        """
        Check if summary should be sent (are there decisions today?)
        Note: We send even if no decisions, with a different message
        
        Returns:
            Always True (we always send daily summary)
        """
        return True
    
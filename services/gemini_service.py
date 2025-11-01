"""
Gemini AI integration for validation and summarization
"""
import google.generativeai as genai
import json
from app.config import get_settings
from app.models import ValidationResult, Decision
from typing import List

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel('gemini-2.5-pro')


async def validate_decision(text: str) -> ValidationResult:
    """
    Validate if text is a meaningful decision using Gemini
    
    Args:
        text: The decision text to validate
        
    Returns:
        ValidationResult with is_valid flag and reason
    """
    prompt = f"""
Analyze if this is a valid team decision statement:
"{text}"

A valid decision should:
- Be a clear, actionable statement
- Make sense in a team/work context
- Not be gibberish, random characters, or nonsensical
- Be at least 3 words long
- Contain meaningful content

Respond ONLY with valid JSON in this exact format:
{{"is_valid": true, "reason": "Brief explanation of why it's valid or invalid"}}

Examples:
- "Use PostgreSQL for database" → {{"is_valid": true, "reason": "Clear technical decision"}}
- "asdfkjh" → {{"is_valid": false, "reason": "Random characters with no meaning"}}
- "ok" → {{"is_valid": false, "reason": "Too vague and short"}}
"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result_dict = json.loads(result_text)
        
        return ValidationResult(
            is_valid=result_dict.get("is_valid", False),
            reason=result_dict.get("reason", "Unknown")
        )
    
    except Exception as e:
        # Fallback validation if Gemini fails
        print(f"⚠️ Gemini validation error: {e}")
        return fallback_validation(text)


def fallback_validation(text: str) -> ValidationResult:
    """
    Basic validation if Gemini fails
    """
    text = text.strip()
    
    # Check minimum length
    if len(text.split()) < 3:
        return ValidationResult(
            is_valid=False,
            reason="Decision is too short (minimum 3 words required)"
        )
    
    # Check for mostly alphabetic characters
    letters = sum(c.isalpha() or c.isspace() for c in text)
    if letters / max(len(text), 1) < 0.6:
        return ValidationResult(
            is_valid=False,
            reason="Text contains too many non-alphabetic characters"
        )
    
    # Check for common decision keywords
    decision_keywords = [
        "use", "adopt", "switch", "choose", "decide", "implement",
        "deploy", "move", "change", "upgrade", "select", "go with",
        "will", "should", "agreed", "approve"
    ]
    
    text_lower = text.lower()
    has_keyword = any(keyword in text_lower for keyword in decision_keywords)
    
    if has_keyword:
        return ValidationResult(
            is_valid=True,
            reason="Contains decision-related keywords"
        )
    
    # If no keywords but passes basic checks, allow it
    return ValidationResult(
        is_valid=True,
        reason="Passes basic validation checks"
    )


async def generate_daily_summary(decisions: List[Decision], date: str) -> str:
    """
    Generate AI-powered daily summary of decisions
    
    Args:
        decisions: List of Decision objects from today
        date: Date string for the summary
        
    Returns:
        AI-generated summary text
    """
    if not decisions:
        return f"📊 Daily Decision Summary - {date}\n\nNo decisions were recorded today. Keep the momentum going! 💪"
    
    # Format decisions for prompt
    decisions_text = "\n".join([
        f"{i+1}. \"{d.text}\" (by {d.user}, {d.timestamp.strftime('%I:%M %p')})"
        for i, d in enumerate(decisions)
    ])
    
    prompt = f"""
You are a team assistant for DecisionNote. Create a concise, insightful daily summary.

Today's date: {date}
Number of decisions: {len(decisions)}

Decisions made today:
{decisions_text}

Write a natural, engaging 2-3 sentence summary that:
1. Highlights key themes or patterns
2. Notes any strategic implications
3. Sounds encouraging and team-friendly
4. Does NOT just list the decisions (they'll be shown separately)

Keep it professional but warm. Focus on insights, not repetition.
"""

    try:
        response = model.generate_content(prompt)
        ai_summary = response.text.strip()
        
        # Format final summary
        formatted_summary = f"""📊 Daily Decision Summary - {date}

{ai_summary}

Today's Decisions ({len(decisions)}):
{decisions_text}
"""
        
        return formatted_summary
    
    except Exception as e:
        print(f"⚠️ Gemini summary error: {e}")
        # Fallback to basic summary
        return f"""📊 Daily Decision Summary - {date}

{len(decisions)} decisions were recorded today.

Decisions:
{decisions_text}
"""
    
"""
Core decision management service
"""
from app.database import execute_query, execute_insert
from app.models import Decision, DecisionHistory
from typing import List, Optional
from datetime import datetime, timedelta
import json


class DecisionService:
    """
    Service for managing decisions
    """
    
    @staticmethod
    async def add_decision(text: str, user: str, topic: Optional[str] = None) -> Decision:
        """
        Add a new decision to the database
        """
        query = """
        INSERT INTO decisions (text, original_text, user, topic)
        VALUES (?, ?, ?, ?)
        """
        
        decision_id = await execute_insert(query, (text, text, user, topic))
        
        return Decision(
            id=decision_id,
            text=text,
            original_text=text,
            user=user,
            topic=topic,
            timestamp=datetime.now()
        )
    
    @staticmethod
    async def get_decision_by_id(decision_id: int) -> Optional[Decision]:
        """
        Get a decision by ID
        """
        query = "SELECT * FROM decisions WHERE id = ?"
        result = await execute_query(query, (decision_id,), fetch_one=True)
        
        if not result:
            return None
        
        return Decision(
            id=result['id'],
            text=result['text'],
            original_text=result['original_text'],
            user=result['user'],
            last_edited_by=result['last_edited_by'],
            last_edited_at=datetime.fromisoformat(result['last_edited_at']) if result['last_edited_at'] else None,
            timestamp=datetime.fromisoformat(result['timestamp']),
            edit_count=result['edit_count'],
            topic=result['topic']
        )
    
    @staticmethod
    async def get_all_decisions(limit: int = 50) -> List[Decision]:
        """
        Get all decisions (most recent first)
        """
        query = "SELECT * FROM decisions ORDER BY timestamp DESC LIMIT ?"
        results = await execute_query(query, (limit,))
        
        return [
            Decision(
                id=row['id'],
                text=row['text'],
                original_text=row['original_text'],
                user=row['user'],
                last_edited_by=row['last_edited_by'],
                last_edited_at=datetime.fromisoformat(row['last_edited_at']) if row['last_edited_at'] else None,
                timestamp=datetime.fromisoformat(row['timestamp']),
                edit_count=row['edit_count'],
                topic=row['topic']
            )
            for row in results
        ]
    
    @staticmethod
    async def search_decisions(query: str) -> List[Decision]:
        """
        Search decisions by keyword
        """
        sql_query = """
        SELECT * FROM decisions 
        WHERE text LIKE ? OR topic LIKE ?
        ORDER BY timestamp DESC
        """
        search_pattern = f"%{query}%"
        results = await execute_query(sql_query, (search_pattern, search_pattern))
        
        return [
            Decision(
                id=row['id'],
                text=row['text'],
                original_text=row['original_text'],
                user=row['user'],
                last_edited_by=row['last_edited_by'],
                last_edited_at=datetime.fromisoformat(row['last_edited_at']) if row['last_edited_at'] else None,
                timestamp=datetime.fromisoformat(row['timestamp']),
                edit_count=row['edit_count'],
                topic=row['topic']
            )
            for row in results
        ]
    
    @staticmethod
    async def update_decision(decision_id: int, new_text: str, editor: str) -> Optional[Decision]:
        """
        Update an existing decision
        """
        # First, get the current decision
        decision = await DecisionService.get_decision_by_id(decision_id)
        
        if not decision:
            return None
        
        # Save to history
        history_query = """
        INSERT INTO decision_history (decision_id, text, edited_by)
        VALUES (?, ?, ?)
        """
        await execute_insert(history_query, (decision_id, decision.text, editor))
        
        # Update the decision
        update_query = """
        UPDATE decisions 
        SET text = ?, 
            last_edited_by = ?, 
            last_edited_at = ?,
            edit_count = edit_count + 1
        WHERE id = ?
        """
        
        now = datetime.now()
        await execute_query(update_query, (new_text, editor, now.isoformat(), decision_id))
        
        # Return updated decision
        decision.text = new_text
        decision.last_edited_by = editor
        decision.last_edited_at = now
        decision.edit_count += 1
        
        return decision
    
    @staticmethod
    async def get_decision_history(decision_id: int) -> List[DecisionHistory]:
        """
        Get edit history for a decision
        """
        query = """
        SELECT * FROM decision_history 
        WHERE decision_id = ? 
        ORDER BY edited_at DESC
        """
        results = await execute_query(query, (decision_id,))
        
        return [
            DecisionHistory(
                id=row['id'],
                decision_id=row['decision_id'],
                text=row['text'],
                edited_by=row['edited_by'],
                edited_at=datetime.fromisoformat(row['edited_at'])
            )
            for row in results
        ]
    
    @staticmethod
    async def get_decisions_by_date_range(start_date: datetime, end_date: datetime) -> List[Decision]:
        """
        Get decisions within a date range
        """
        query = """
        SELECT * FROM decisions 
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
        """
        
        results = await execute_query(
            query, 
            (start_date.isoformat(), end_date.isoformat())
        )
        
        return [
            Decision(
                id=row['id'],
                text=row['text'],
                original_text=row['original_text'],
                user=row['user'],
                last_edited_by=row['last_edited_by'],
                last_edited_at=datetime.fromisoformat(row['last_edited_at']) if row['last_edited_at'] else None,
                timestamp=datetime.fromisoformat(row['timestamp']),
                edit_count=row['edit_count'],
                topic=row['topic']
            )
            for row in results
        ]
    
    @staticmethod
    async def get_todays_decisions() -> List[Decision]:
        """
        Get all decisions made today
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        return await DecisionService.get_decisions_by_date_range(today_start, today_end)
    
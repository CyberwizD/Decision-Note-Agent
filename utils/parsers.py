"""
Command parsing utilities
"""
import re
from typing import Optional, Tuple


class CommandParser:
    """
    Parse user commands for DecisionNote
    """
    
    @staticmethod
    def parse_command(message: str) -> Tuple[str, Optional[str]]:
        """
        Parse command from message.
        
        Returns:
            (command, argument)
            
        Examples:
            "add Use MongoDB" → ("add", "Use MongoDB")
            "list" → ("list", None)
            "search backend" → ("search", "backend")
        """
        message = message.strip()

        # Remove /decision prefix if present
        if message.startswith("/decision"):
            message = message[9:].strip()
        
        # Split into command and the rest of the string
        parts = message.split(maxsplit=1)
        
        if not parts:
            return ("unknown", None)
        
        command = parts[0].lower()
        argument = parts[1].strip() if len(parts) > 1 else None
        
        return (command, argument)
    
    @staticmethod
    def extract_decision_text(message: str) -> str:
        """
        Extract decision text from add/propose command
        
        Handles quotes and various formats:
            add "Use MongoDB"
            add Use MongoDB
            propose "Switch to React"
        """
        # Remove command prefix
        _, text = CommandParser.parse_command(message)
        
        if not text:
            return ""
        
        # Remove quotes if present
        text = text.strip()
        if (text.startswith('"') and text.endswith('"')) or \
           (text.startswith("'") and text.endswith("'")):
            text = text[1:-1]
        
        return text.strip()
    
    @staticmethod
    def parse_edit_command(message: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Parse edit command to extract decision ID and new text
        
        Examples:
            "edit 5 New text" → (5, "New text")
            "edit 3 "Use PostgreSQL"" → (3, "Use PostgreSQL")
        """
        _, argument = CommandParser.parse_command(message)
        
        if not argument:
            return (None, None)
        
        # Split into ID and text
        parts = argument.split(maxsplit=1)
        
        if len(parts) < 2:
            return (None, None)
        
        try:
            decision_id = int(parts[0])
            text = parts[1].strip()
            
            # Remove quotes if present
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith("'") and text.endswith("'")):
                text = text[1:-1]
            
            return (decision_id, text.strip())
        
        except ValueError:
            return (None, None)
    
    @staticmethod
    def parse_search_query(message: str) -> str:
        """
        Extract search query from search command
        """
        _, query = CommandParser.parse_command(message)
        return query.strip() if query else ""
    
    @staticmethod
    def parse_vote_command(message: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Parse vote command to extract proposal ID and vote type
        
        Examples:
            "approve 3" → (3, "approve")
            "reject 5" → (5, "reject")
        """
        command, argument = CommandParser.parse_command(message)
        
        if command not in ["approve", "reject"]:
            return (None, None)
        
        if not argument:
            return (None, None)
        
        try:
            proposal_id = int(argument.strip())
            return (proposal_id, command)
        except ValueError:
            return (None, None)

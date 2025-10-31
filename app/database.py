"""
Database connection and initialization
"""
import aiosqlite
import os
from pathlib import Path
from app.schemas import (
    CREATE_DECISIONS_TABLE,
    CREATE_PROPOSED_DECISIONS_TABLE,
    CREATE_DECISION_HISTORY_TABLE,
    CREATE_DECISIONS_INDEX,
    CREATE_DECISIONS_USER_INDEX,
    CREATE_PROPOSED_STATUS_INDEX
)

# Database file path
DB_DIR = Path("data")
DB_PATH = DB_DIR / "decisionnote.db"


async def get_db():
    """
    Get database connection (async context manager)
    """
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row  # Enable column access by name
    try:
        yield db
    finally:
        await db.close()


async def init_database():
    """
    Initialize database with required tables
    """
    # Create data directory if it doesn't exist
    DB_DIR.mkdir(exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Create tables
        await db.execute(CREATE_DECISIONS_TABLE)
        await db.execute(CREATE_PROPOSED_DECISIONS_TABLE)
        await db.execute(CREATE_DECISION_HISTORY_TABLE)
        
        # Create indexes
        await db.execute(CREATE_DECISIONS_INDEX)
        await db.execute(CREATE_DECISIONS_USER_INDEX)
        await db.execute(CREATE_PROPOSED_STATUS_INDEX)
        
        await db.commit()
        print("✅ Database initialized successfully")


async def execute_query(query: str, params: tuple = (), fetch_one: bool = False):
    """
    Execute a database query
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query, params)
        
        if fetch_one:
            result = await cursor.fetchone()
        else:
            result = await cursor.fetchall()
        
        await db.commit()
        return result


async def execute_insert(query: str, params: tuple = ()):
    """
    Execute an INSERT query and return the last inserted row ID
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.lastrowid
        
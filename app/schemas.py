"""
Database schemas for DecisionNote Agent
"""

# SQL statements for creating tables

CREATE_DECISIONS_TABLE = """
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    original_text TEXT,
    user TEXT NOT NULL,
    last_edited_by TEXT,
    last_edited_at DATETIME,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    edit_count INTEGER DEFAULT 0,
    topic TEXT,
    metadata TEXT
);
"""

CREATE_PROPOSED_DECISIONS_TABLE = """
CREATE TABLE IF NOT EXISTS proposed_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    proposer TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    approvals TEXT DEFAULT '[]',
    rejections TEXT DEFAULT '[]',
    status TEXT DEFAULT 'pending',
    threshold INTEGER DEFAULT 2,
    expires_at DATETIME
);
"""

CREATE_DECISION_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS decision_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    edited_by TEXT NOT NULL,
    edited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES decisions (id)
);
"""

# Index for faster queries
CREATE_DECISIONS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_decisions_timestamp 
ON decisions(timestamp DESC);
"""

CREATE_DECISIONS_USER_INDEX = """
CREATE INDEX IF NOT EXISTS idx_decisions_user 
ON decisions(user);
"""

CREATE_PROPOSED_STATUS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_proposed_status 
ON proposed_decisions(status);
"""

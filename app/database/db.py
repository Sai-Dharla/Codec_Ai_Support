import os
import sqlite3
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

def init_db(db_path: str):
    """Initializes the SQLite database tables if they do not exist."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context_topic TEXT
            )
        """)
        
        # Interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                intent_detected TEXT,
                confidence REAL,
                context_topic TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # Indexes for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)")
        conn.commit()

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        init_db(db_path)

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def create_or_update_session(self, session_id: str, context_topic: Optional[str] = None):
        """Creates a new session or updates last_active timestamp and context_topic."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO sessions (session_id, created_at, last_active, context_topic)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    last_active = excluded.last_active,
                    context_topic = COALESCE(excluded.context_topic, sessions.context_topic)
                """,
                (session_id, now, now, context_topic)
            )

    def log_interaction(
        self,
        session_id: str,
        user_message: str,
        bot_response: str,
        intent_detected: Optional[str] = None,
        confidence: Optional[float] = None,
        context_topic: Optional[str] = None
    ):
        """Persists a complete turn in the interactions table."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO sessions (session_id, created_at, last_active, context_topic)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    last_active = excluded.last_active,
                    context_topic = COALESCE(excluded.context_topic, sessions.context_topic)
                """,
                (session_id, now, now, context_topic)
            )
            
            cursor.execute(
                """
                INSERT INTO interactions (session_id, user_message, bot_response, intent_detected, confidence, context_topic, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, user_message, bot_response, intent_detected, confidence, context_topic, now)
            )

    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves interaction logs for a given session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, session_id, user_message, bot_response, intent_detected, confidence, context_topic, timestamp
                FROM interactions
                WHERE session_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
                """,
                (session_id, limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_session_context(self, session_id: str) -> Optional[str]:
        """Retrieves the active context topic for a given session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT context_topic FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return row['context_topic'] if row else None


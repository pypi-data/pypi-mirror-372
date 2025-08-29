"""Session management with SQLite integration for conversation storage."""

import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Message:
    """Conversation message."""
    id: Optional[int]
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    tokens_used: Optional[int] = None


@dataclass
class Session:
    """Conversation session."""
    id: Optional[int]
    session_id: str
    workspace_name: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    message_count: int = 0


@dataclass
class ExtractedInsight:
    """Extracted insight from conversation."""
    id: Optional[int]
    session_id: str
    insight_type: str  # 'preference', 'knowledge', 'pattern'
    target_layer: str  # 'global' or 'workspace'
    content: str
    confidence: float
    applied_at: Optional[datetime] = None


class SessionManagerError(Exception):
    """Session manager related errors."""
    pass


class SessionManager:
    """Manages conversation sessions and SQLite storage."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / ".memory-chatbot" / "sessions.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[Session] = None
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        workspace_name TEXT,
                        started_at DATETIME NOT NULL,
                        ended_at DATETIME,
                        message_count INTEGER DEFAULT 0
                    );
                    
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        tokens_used INTEGER,
                        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                    );
                    
                    CREATE TABLE IF NOT EXISTS extracted_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        insight_type TEXT NOT NULL,
                        target_layer TEXT NOT NULL,
                        content TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        applied_at DATETIME,
                        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
                    CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
                    CREATE INDEX IF NOT EXISTS idx_insights_session ON extracted_insights(session_id);
                """)
                conn.commit()
        except Exception as e:
            raise SessionManagerError(f"Failed to initialize database: {e}")
    
    def start_session(self, workspace_name: Optional[str] = None) -> Session:
        """Start a new conversation session."""
        session_id = str(uuid.uuid4())
        session = Session(
            id=None,
            session_id=session_id,
            workspace_name=workspace_name,
            started_at=datetime.now(),
            ended_at=None
        )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (session_id, workspace_name, started_at, message_count)
                    VALUES (?, ?, ?, 0)
                """, (session.session_id, session.workspace_name, session.started_at))
                session.id = cursor.lastrowid
                conn.commit()
        except Exception as e:
            raise SessionManagerError(f"Failed to start session: {e}")
        
        self.current_session = session
        return session
    
    def end_session(self, session_id: Optional[str] = None) -> None:
        """End a conversation session."""
        target_session_id = session_id or (self.current_session.session_id if self.current_session else None)
        if not target_session_id:
            raise SessionManagerError("No session to end")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions 
                    SET ended_at = ? 
                    WHERE session_id = ?
                """, (datetime.now(), target_session_id))
                conn.commit()
        except Exception as e:
            raise SessionManagerError(f"Failed to end session: {e}")
        
        if self.current_session and self.current_session.session_id == target_session_id:
            self.current_session = None
    
    def add_message(self, role: str, content: str, tokens_used: Optional[int] = None, 
                   session_id: Optional[str] = None) -> Message:
        """Add a message to the current session."""
        target_session_id = session_id or (self.current_session.session_id if self.current_session else None)
        if not target_session_id:
            raise SessionManagerError("No active session")
        
        if role not in ['user', 'assistant']:
            raise SessionManagerError(f"Invalid role: {role}")
        
        message = Message(
            id=None,
            session_id=target_session_id,
            role=role,
            content=content,
            timestamp=datetime.now(),
            tokens_used=tokens_used
        )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (session_id, role, content, timestamp, tokens_used)
                    VALUES (?, ?, ?, ?, ?)
                """, (message.session_id, message.role, message.content, 
                     message.timestamp, message.tokens_used))
                message.id = cursor.lastrowid
                
                # Update session message count
                cursor.execute("""
                    UPDATE sessions 
                    SET message_count = message_count + 1 
                    WHERE session_id = ?
                """, (target_session_id,))
                
                conn.commit()
        except Exception as e:
            raise SessionManagerError(f"Failed to add message: {e}")
        
        return message
    
    def get_session_messages(self, session_id: Optional[str] = None, limit: Optional[int] = None) -> List[Message]:
        """Get messages for a session."""
        target_session_id = session_id or (self.current_session.session_id if self.current_session else None)
        if not target_session_id:
            raise SessionManagerError("No session specified")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = """
                    SELECT id, session_id, role, content, timestamp, tokens_used 
                    FROM messages 
                    WHERE session_id = ? 
                    ORDER BY timestamp
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query, (target_session_id,))
                rows = cursor.fetchall()
                
                return [
                    Message(
                        id=row[0],
                        session_id=row[1],
                        role=row[2],
                        content=row[3],
                        timestamp=datetime.fromisoformat(row[4]),
                        tokens_used=row[5]
                    )
                    for row in rows
                ]
        except Exception as e:
            raise SessionManagerError(f"Failed to get messages: {e}")
    
    def get_recent_context(self, session_id: Optional[str] = None, 
                          max_messages: int = 10, max_tokens: int = 4000) -> List[Dict[str, str]]:
        """Get recent conversation context for LLM input."""
        messages = self.get_session_messages(session_id, limit=max_messages * 2)  # Get more to filter
        
        # Convert to format expected by LLM providers
        context = []
        total_tokens = 0
        
        for message in reversed(messages):  # Start from most recent
            # Rough token estimation (4 characters per token)
            estimated_tokens = len(message.content) // 4
            if total_tokens + estimated_tokens > max_tokens:
                break
            
            context.append({
                "role": message.role,
                "content": message.content
            })
            total_tokens += estimated_tokens
            
            if len(context) >= max_messages:
                break
        
        # Return in chronological order
        return list(reversed(context))
    
    def get_workspace_history(self, workspace_name: str, max_messages: int = 50) -> List[Dict[str, str]]:
        """Get recent conversation history for entire workspace (across all sessions)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Get messages from all sessions in the workspace, ordered by timestamp
                query = """
                    SELECT m.role, m.content, m.timestamp, s.session_id
                    FROM messages m
                    JOIN sessions s ON m.session_id = s.session_id
                    WHERE s.workspace_name = ?
                    ORDER BY m.timestamp DESC
                    LIMIT ?
                """
                
                cursor.execute(query, (workspace_name, max_messages))
                rows = cursor.fetchall()
                
                # Convert to format expected by debug display
                history = []
                for row in rows:
                    history.append({
                        "role": row[0],
                        "content": row[1],
                        "timestamp": row[2],
                        "session_id": row[3]
                    })
                
                # Return in reverse chronological order (most recent first for debug display)
                return history
                
        except sqlite3.Error as e:
            print(f"Database error getting workspace history: {e}")
            return []
    
    def add_extracted_insight(self, insight_type: str, target_layer: str, 
                            content: str, confidence: float, 
                            session_id: Optional[str] = None) -> ExtractedInsight:
        """Add an extracted insight from the conversation."""
        target_session_id = session_id or (self.current_session.session_id if self.current_session else None)
        if not target_session_id:
            raise SessionManagerError("No active session")
        
        if insight_type not in ['preference', 'knowledge', 'pattern']:
            raise SessionManagerError(f"Invalid insight type: {insight_type}")
        
        if target_layer not in ['global', 'workspace']:
            raise SessionManagerError(f"Invalid target layer: {target_layer}")
        
        if not 0.0 <= confidence <= 1.0:
            raise SessionManagerError("Confidence must be between 0.0 and 1.0")
        
        insight = ExtractedInsight(
            id=None,
            session_id=target_session_id,
            insight_type=insight_type,
            target_layer=target_layer,
            content=content,
            confidence=confidence
        )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO extracted_insights 
                    (session_id, insight_type, target_layer, content, confidence)
                    VALUES (?, ?, ?, ?, ?)
                """, (insight.session_id, insight.insight_type, insight.target_layer,
                     insight.content, insight.confidence))
                insight.id = cursor.lastrowid
                conn.commit()
        except Exception as e:
            raise SessionManagerError(f"Failed to add insight: {e}")
        
        return insight
    
    def get_pending_insights(self, min_confidence: float = 0.5) -> List[ExtractedInsight]:
        """Get insights that haven't been applied yet."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_id, insight_type, target_layer, content, confidence
                    FROM extracted_insights 
                    WHERE applied_at IS NULL AND confidence >= ?
                    ORDER BY confidence DESC
                """, (min_confidence,))
                rows = cursor.fetchall()
                
                return [
                    ExtractedInsight(
                        id=row[0],
                        session_id=row[1],
                        insight_type=row[2],
                        target_layer=row[3],
                        content=row[4],
                        confidence=row[5]
                    )
                    for row in rows
                ]
        except Exception as e:
            raise SessionManagerError(f"Failed to get pending insights: {e}")
    
    def mark_insight_applied(self, insight_id: int) -> None:
        """Mark an insight as applied to memory."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE extracted_insights 
                    SET applied_at = ? 
                    WHERE id = ?
                """, (datetime.now(), insight_id))
                conn.commit()
        except Exception as e:
            raise SessionManagerError(f"Failed to mark insight as applied: {e}")
    
    def get_sessions(self, workspace_name: Optional[str] = None, 
                    limit: int = 50) -> List[Session]:
        """Get session list, optionally filtered by workspace."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if workspace_name:
                    cursor.execute("""
                        SELECT id, session_id, workspace_name, started_at, ended_at, message_count
                        FROM sessions 
                        WHERE workspace_name = ?
                        ORDER BY started_at DESC 
                        LIMIT ?
                    """, (workspace_name, limit))
                else:
                    cursor.execute("""
                        SELECT id, session_id, workspace_name, started_at, ended_at, message_count
                        FROM sessions 
                        ORDER BY started_at DESC 
                        LIMIT ?
                    """, (limit,))
                
                rows = cursor.fetchall()
                
                return [
                    Session(
                        id=row[0],
                        session_id=row[1],
                        workspace_name=row[2],
                        started_at=datetime.fromisoformat(row[3]),
                        ended_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        message_count=row[5]
                    )
                    for row in rows
                ]
        except Exception as e:
            raise SessionManagerError(f"Failed to get sessions: {e}")
    
    def clean_old_sessions(self, days_threshold: int = 90) -> int:
        """Clean old session data."""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get sessions to delete
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id FROM sessions 
                    WHERE started_at < ?
                """, (cutoff_date,))
                old_sessions = [row[0] for row in cursor.fetchall()]
                
                if not old_sessions:
                    return 0
                
                # Delete related data
                placeholders = ','.join('?' * len(old_sessions))
                cursor.execute(f"""
                    DELETE FROM messages 
                    WHERE session_id IN ({placeholders})
                """, old_sessions)
                
                cursor.execute(f"""
                    DELETE FROM extracted_insights 
                    WHERE session_id IN ({placeholders})
                """, old_sessions)
                
                cursor.execute(f"""
                    DELETE FROM sessions 
                    WHERE session_id IN ({placeholders})
                """, old_sessions)
                
                conn.commit()
                return len(old_sessions)
                
        except Exception as e:
            raise SessionManagerError(f"Failed to clean old sessions: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM messages")
                total_messages = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM extracted_insights")
                total_insights = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM extracted_insights WHERE applied_at IS NOT NULL")
                applied_insights = cursor.fetchone()[0]
                
                return {
                    "total_sessions": total_sessions,
                    "total_messages": total_messages,
                    "total_insights": total_insights,
                    "applied_insights": applied_insights,
                    "pending_insights": total_insights - applied_insights
                }
        except Exception as e:
            raise SessionManagerError(f"Failed to get stats: {e}")
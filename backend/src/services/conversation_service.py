from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
from ..models.conversation_session import ConversationSession
from ..models.conversation_turn import ConversationTurn
from ..models.academic_query import AcademicQuery
from ..models.textbook_response import TextbookResponse


class ConversationService:
    """
    Service for managing conversation sessions and history
    """

    def __init__(self, session_ttl_hours: int = 24):
        self.sessions: Dict[str, ConversationSession] = {}
        self.session_ttl = timedelta(hours=session_ttl_hours)

    def create_session(self, user_id: Optional[str] = None) -> ConversationSession:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()

        session = ConversationSession(
            session_id=session_id,
            created_at=now,
            last_accessed=now,
            expires_at=now + self.session_ttl,
            user_id=user_id,
            history=[]
        )

        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get an existing session by ID"""
        session = self.sessions.get(session_id)
        if session and datetime.now() > session.expires_at:
            # Session expired, remove it
            del self.sessions[session_id]
            return None
        return session

    def add_turn_to_session(self, session_id: str, turn: ConversationTurn) -> bool:
        """Add a conversation turn to a session"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.history.append(turn)
        session.last_accessed = datetime.now()
        return True

    def get_recent_history(self, session_id: str, max_turns: int = 10) -> List[ConversationTurn]:
        """Get recent conversation history for context injection"""
        session = self.get_session(session_id)
        if not session:
            return []

        # Return the most recent turns up to max_turns
        return session.history[-max_turns:]

    def clear_session_history(self, session_id: str) -> bool:
        """Clear conversation history while keeping the session active"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.history = []
        session.last_accessed = datetime.now()
        return True

    def cleanup_expired_sessions(self):
        """Remove all expired sessions"""
        now = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if now > session.expires_at
        ]

        for session_id in expired_sessions:
            del self.sessions[session_id]
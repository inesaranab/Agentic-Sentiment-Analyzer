"""Session and conversation management for YouTube sentiment analysis.

This module manages:
- Conversation threads with persistent memory
- Video data caching for follow-up questions
- Session lifecycle (creation, retrieval, cleanup)
"""

import uuid
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from langchain_core.documents import Document


@dataclass
class VideoSession:
    """Represents a video analysis session with conversation history.
    
    Attributes:
        session_id: Unique identifier for the conversation thread
        video_id: YouTube video ID being analyzed
        video_title: Video title
        channel_name: Channel name
        created_at: Session creation timestamp
        last_accessed: Last access timestamp
        main_graph: Compiled LangGraph with memory checkpointer
        documents: Cached documents for retrieval
        bm25_retriever: Cached BM25 retriever
        raw_blobs: Cached raw video data (transcript, comments, etc.)
    """
    session_id: str
    video_id: str
    video_title: str
    channel_name: str
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    main_graph: Any = None
    documents: list[Document] = field(default_factory=list)
    bm25_retriever: Any = None
    raw_blobs: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Manages video analysis sessions and conversation threads.
    
    This class provides:
    - Session creation for new video analyses
    - Session retrieval for follow-up questions
    - Automatic session cleanup (TTL-based)
    - Thread-scoped conversation memory
    """
    
    def __init__(self, session_ttl_hours: int = 24):
        """Initialize session manager.
        
        Args:
            session_ttl_hours: Time-to-live for sessions in hours (default: 24)
        """
        self._sessions: Dict[str, VideoSession] = {}
        self._session_ttl = timedelta(hours=session_ttl_hours)
    
    def create_session(
        self,
        video_id: str,
        video_title: str,
        channel_name: str
    ) -> str:
        """Create a new video analysis session.
        
        Args:
            video_id: YouTube video ID
            video_title: Video title
            channel_name: Channel name
            
        Returns:
            Unique session ID (thread_id) for this conversation
        """
        session_id = str(uuid.uuid4())
        session = VideoSession(
            session_id=session_id,
            video_id=video_id,
            video_title=video_title,
            channel_name=channel_name
        )
        self._sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[VideoSession]:
        """Retrieve an existing session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            VideoSession if found and not expired, None otherwise
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        # Check if session has expired
        if datetime.now() - session.last_accessed > self._session_ttl:
            self.delete_session(session_id)
            return None
        
        # Update last accessed time
        session.last_accessed = datetime.now()
        return session
    
    def update_session(
        self,
        session_id: str,
        main_graph: Any = None,
        documents: list[Document] = None,
        bm25_retriever: Any = None,
        raw_blobs: Dict[str, Any] = None
    ):
        """Update session with analysis artifacts.
        
        Args:
            session_id: Session identifier
            main_graph: Compiled LangGraph with checkpointer
            documents: Retrieved documents
            bm25_retriever: BM25 retriever instance
            raw_blobs: Raw video data
        """
        session = self._sessions.get(session_id)
        if not session:
            return
        
        if main_graph is not None:
            session.main_graph = main_graph
        if documents is not None:
            session.documents = documents
        if bm25_retriever is not None:
            session.bm25_retriever = bm25_retriever
        if raw_blobs is not None:
            session.raw_blobs = raw_blobs
        
        session.last_accessed = datetime.now()
    
    def delete_session(self, session_id: str):
        """Delete a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove all expired sessions.
        
        This should be called periodically (e.g., via background task).
        """
        now = datetime.now()
        expired_ids = [
            sid for sid, session in self._sessions.items()
            if now - session.last_accessed > self._session_ttl
        ]
        
        for sid in expired_ids:
            self.delete_session(sid)
    
    def list_active_sessions(self) -> list[Dict[str, Any]]:
        """List all active sessions.
        
        Returns:
            List of session metadata
        """
        return [
            {
                "session_id": session.session_id,
                "video_id": session.video_id,
                "video_title": session.video_title,
                "channel_name": session.channel_name,
                "created_at": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat()
            }
            for session in self._sessions.values()
        ]


# Global session manager instance
session_manager = SessionManager()

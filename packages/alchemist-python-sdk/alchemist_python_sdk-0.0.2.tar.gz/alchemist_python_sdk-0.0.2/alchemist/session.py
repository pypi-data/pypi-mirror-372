"""
Session management for Alchemist agent conversations.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Iterator
from dataclasses import dataclass
from datetime import datetime

from .exceptions import SessionError, ValidationError
from .utils import sanitize_message, extract_error_message

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }


@dataclass
class ChatResponse:
    """Response from agent chat interaction."""
    text: str
    session_id: str
    token_usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'text': self.text,
            'session_id': self.session_id,
            'token_usage': self.token_usage,
            'metadata': self.metadata or {},
            'success': self.success,
            'error': self.error
        }


class Session:
    """
    Represents a conversation session with an Alchemist agent.
    
    Sessions provide persistent conversation context and history management.
    Each session maintains its own conversation thread with the agent.
    
    Args:
        session_id: Unique identifier for this session
        agent: Reference to the parent Agent instance
        user_id: Optional user identifier
        metadata: Optional session metadata
    """
    
    def __init__(
        self,
        session_id: str,
        agent_client: 'AgentClient',  # Forward reference to AgentClient
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id
        self.agent_client = agent_client
        self.user_id = user_id or "sdk_user"
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        logger.debug(f"Created session {session_id} for agent {agent_client.agent_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for this session.
        
        Returns:
            Dictionary containing session statistics
        """
        try:
            # Try to get stats from agent service
            return self.agent_client._get_session_stats(self.session_id)
        except Exception as e:
            logger.error(f"Failed to get session stats: {str(e)}")
            # Return basic session info if service stats fail
            return {
                'session_id': self.session_id,
                'created_at': self.created_at.isoformat(),
                'last_activity': self.last_activity.isoformat(),
                'user_id': self.user_id,
                'metadata': self.metadata
            }
    
    def __repr__(self) -> str:
        return f"Session(id={self.session_id}, agent={self.agent_client.agent_id}, user={self.user_id})"
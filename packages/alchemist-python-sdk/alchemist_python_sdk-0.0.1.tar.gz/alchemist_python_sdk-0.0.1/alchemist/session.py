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
        
        # Local message history cache
        self._message_cache: List[Message] = []
        
        logger.debug(f"Created session {session_id} for agent {agent_client.agent_id}")
    
    def send_message(
        self,
        message: str,
        stream: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        Send a message to the agent in this session.
        
        Args:
            message: The message text to send
            stream: Whether to enable streaming response (default: False)
            metadata: Optional message metadata
            
        Returns:
            ChatResponse containing the agent's response
            
        Raises:
            SessionError: If the message fails to send
            ValidationError: If the message is invalid
        """
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        message = sanitize_message(message)
        self.last_activity = datetime.now()
        
        try:
            # Add user message to cache
            user_message = Message(
                role='user',
                content=message,
                timestamp=datetime.now(),
                metadata=metadata
            )
            self._message_cache.append(user_message)
            
            # Send message through agent client
            if stream:
                # For streaming, return an iterator-like response
                return self._handle_streaming_response(message, metadata)
            else:
                response = self.agent_client._send_session_message(
                    session_id=self.session_id,
                    message=message,
                    user_id=self.user_id,
                    metadata=metadata
                )
                
                # Add assistant response to cache
                assistant_message = Message(
                    role='assistant',
                    content=response.text,
                    timestamp=datetime.now(),
                    metadata=response.metadata
                )
                self._message_cache.append(assistant_message)
                
                return response
                
        except Exception as e:
            logger.error(f"Failed to send message in session {self.session_id}: {str(e)}")
            raise SessionError(f"Failed to send message: {str(e)}")
    
    def stream_message(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Iterator[str]:
        """
        Send a message and stream the response.
        
        Args:
            message: The message text to send
            metadata: Optional message metadata
            
        Yields:
            String chunks of the agent's response
            
        Raises:
            SessionError: If streaming fails
            ValidationError: If the message is invalid
        """
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        message = sanitize_message(message)
        self.last_activity = datetime.now()
        
        try:
            # Add user message to cache
            user_message = Message(
                role='user',
                content=message,
                timestamp=datetime.now(),
                metadata=metadata
            )
            self._message_cache.append(user_message)
            
            # Stream response from agent client
            full_response = ""
            for chunk in self.agent_client._stream_session_message(
                session_id=self.session_id,
                message=message,
                user_id=self.user_id,
                metadata=metadata
            ):
                full_response += chunk
                yield chunk
            
            # Add complete assistant response to cache
            if full_response:
                assistant_message = Message(
                    role='assistant',
                    content=full_response,
                    timestamp=datetime.now(),
                    metadata=metadata
                )
                self._message_cache.append(assistant_message)
                
        except Exception as e:
            logger.error(f"Failed to stream message in session {self.session_id}: {str(e)}")
            raise SessionError(f"Failed to stream message: {str(e)}")
    
    def get_history(
        self, 
        limit: int = 50, 
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get the conversation history for this session.
        
        Args:
            limit: Maximum number of messages to return
            include_metadata: Whether to include message metadata
            
        Returns:
            List of message dictionaries
            
        Raises:
            SessionError: If history retrieval fails
        """
        try:
            # First try to get history from the agent service
            try:
                history = self.agent_client._get_session_history(
                    session_id=self.session_id,
                    limit=limit
                )
                
                # Update local cache with server history
                if history:
                    self._update_cache_from_history(history)
                    
                if include_metadata:
                    return history
                else:
                    return [
                        {
                            'role': msg.get('message_info', {}).get('role', 'unknown'), 
                            'content': msg.get('message_info', {}).get('content', '')
                        }
                        for msg in history
                    ]
                
            except Exception as e:
                logger.debug(f"Could not fetch server history, using cache: {str(e)}")
                
                # Fall back to local cache
                messages = self._message_cache[-limit:] if limit > 0 else self._message_cache
                
                if include_metadata:
                    return [msg.to_dict() for msg in messages]
                else:
                    return [
                        {'role': msg.role, 'content': msg.content}
                        for msg in messages
                    ]
                
        except Exception as e:
            logger.error(f"Failed to get session history: {str(e)}")
            raise SessionError(f"Failed to get session history: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for this session.
        
        Returns:
            Dictionary containing session statistics
        """
        try:
            # Try to get stats from agent service
            try:
                return self.agent_client._get_session_stats(self.session_id)
            except Exception:
                # Fall back to local stats
                user_messages = [msg for msg in self._message_cache if msg.role == 'user']
                assistant_messages = [msg for msg in self._message_cache if msg.role == 'assistant']
                
                return {
                    'session_id': self.session_id,
                    'created_at': self.created_at.isoformat(),
                    'last_activity': self.last_activity.isoformat(),
                    'total_messages': len(self._message_cache),
                    'user_messages': len(user_messages),
                    'assistant_messages': len(assistant_messages),
                    'cached_messages': len(self._message_cache)
                }
                
        except Exception as e:
            logger.error(f"Failed to get session stats: {str(e)}")
            raise SessionError(f"Failed to get session stats: {str(e)}")
    
    def clear_history(self) -> bool:
        """
        Clear the conversation history for this session.
        
        Note: This only clears the local cache. The server-side history
        may persist depending on agent configuration.
        
        Returns:
            True if successful
        """
        try:
            self._message_cache.clear()
            logger.debug(f"Cleared local history for session {self.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear session history: {str(e)}")
            raise SessionError(f"Failed to clear session history: {str(e)}")
    
    def _update_cache_from_history(self, history: List[Dict[str, Any]]):
        """Update local message cache from server history."""
        try:
            self._message_cache.clear()
            for msg_data in history:
                # Extract role and content from message_info nested structure
                message_info = msg_data.get('message_info', {})
                message = Message(
                    role=message_info.get('role', 'unknown'),
                    content=message_info.get('content', ''),
                    timestamp=datetime.fromisoformat(
                        message_info.get('timestamp', datetime.now().isoformat())
                    ),
                    metadata=msg_data.get('message_metadata', {})
                )
                self._message_cache.append(message)
                
        except Exception as e:
            logger.warning(f"Failed to update cache from history: {str(e)}")
    
    def _handle_streaming_response(
        self, 
        message: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Handle streaming response for backward compatibility."""
        full_response = ""
        
        try:
            for chunk in self.stream_message(message, metadata):
                full_response += chunk
            
            return ChatResponse(
                text=full_response,
                session_id=self.session_id,
                metadata=metadata,
                success=True
            )
            
        except Exception as e:
            return ChatResponse(
                text="",
                session_id=self.session_id,
                metadata=metadata,
                success=False,
                error=str(e)
            )
    
    def __repr__(self) -> str:
        return f"Session(id={self.session_id}, agent={self.agent_client.agent_id}, messages={len(self._message_cache)})"
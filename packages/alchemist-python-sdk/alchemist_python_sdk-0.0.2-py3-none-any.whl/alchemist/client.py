"""
Agent client class for the Alchemist Python SDK.

This client is designed to interact with a specific Alchemist agent instance.
Each agent has its own API keys, and the service URL is automatically constructed
from the agent_id.
"""

import logging
import json
import time
import requests
from typing import Dict, Any, Optional, Iterator, List
from urllib.parse import urljoin
import uuid

from .session import Session, ChatResponse
from .exceptions import (
    AlchemistError,
    AuthenticationError,
    AgentNotFoundError,
    SessionError,
    NetworkError,
    RateLimitError,
    StreamingError,
    ValidationError
)
from .utils import (
    format_url,
    parse_response_headers,
    retry_with_backoff,
    clean_json_response,
    extract_error_message,
    sanitize_message,
    validate_agent_id,
    validate_api_key
)

logger = logging.getLogger(__name__)


class AgentClient:
    """
    Client for interacting with a specific Alchemist agent.
    
    Each agent has its own deployed service and API keys. This client manages
    sessions for conversations with agents. All messages must be sent through
    sessions - no direct chat methods are available.
    
    Args:
        agent_id: The unique identifier for the agent
        api_key: Agent-specific API key (starts with 'ak_')
        agent_url: The deployed agent service URL (optional - auto-constructed if not provided)
        timeout: Request timeout in seconds (default: 120)
        max_retries: Maximum retry attempts for failed requests (default: 3)
    
    Example:
        >>> client = AgentClient(
        ...     agent_id="agent-123",
        ...     api_key="ak_agent123_your_key_here"
        ... )
        >>> session = client.create_session(user_id="user123")
        >>> response = session.send_message("Hello!")
        >>> print(response.text)
    """
    
    def __init__(
        self,
        agent_id: str,
        api_key: str,
        agent_url: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3
    ):
        if not validate_agent_id(agent_id):
            raise ValueError("Invalid agent ID format")
        
        if not validate_api_key(api_key):
            raise ValueError("Invalid API key format")
        
        if not api_key.startswith('ak_'):
            raise ValueError("API key must start with 'ak_' prefix")
        
        # Auto-construct agent URL if not provided
        if agent_url is None:
            agent_url = f"https://agent-{agent_id}-b3hpe34qdq-uc.a.run.app"
        
        if not agent_url.startswith('https://'):
            raise ValueError("agent_url must be a valid HTTPS URL")
        
        self.agent_id = agent_id
        self.api_key = api_key
        self.agent_url = agent_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'alchemist-python-sdk/1.0.0'
        })
        
        # Cache for active sessions
        self._session_cache: Dict[str, Session] = {}
        
        logger.debug(f"Initialized AgentClient for {agent_id} at {self.agent_url}")
    
    
    
    def create_session(
        self,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new conversation session.
        
        Args:
            user_id: Optional user identifier (default: 'sdk_user')
            metadata: Optional session metadata
            
        Returns:
            Session ID string
            
        Raises:
            SessionError: If session creation fails
        """
        try:
            # Create session on the agent service
            session_data = self._create_agent_session(
                user_id or 'sdk_user', 
                metadata
            )
            session_id = session_data.get('session_id')
            
            if not session_id:
                raise SessionError("No session ID returned from agent service")
            
            logger.debug(f"Created session {session_id} for agent {self.agent_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session for agent {self.agent_id}: {str(e)}")
            raise SessionError(f"Failed to create session: {str(e)}")
    
    def send_message(
        self,
        session_id: str,
        message: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        Send a message to an agent session.
        
        Args:
            session_id: The session ID to send the message to
            message: The message text to send
            user_id: Optional user identifier (default: 'sdk_user')
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
        
        try:
            response = self._send_session_message(
                session_id=session_id,
                message=message,
                user_id=user_id or 'sdk_user',
                metadata=metadata
            )
            
            logger.debug(f"Sent message to session {session_id} for agent {self.agent_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to send message to session {session_id}: {str(e)}")
            raise SessionError(f"Failed to send message: {str(e)}")
    
    def stream_message(
        self,
        session_id: str,
        message: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Iterator[str]:
        """
        Send a message and stream the response.
        
        Args:
            session_id: The session ID to send the message to
            message: The message text to send
            user_id: Optional user identifier (default: 'sdk_user')
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
        
        try:
            for chunk in self._stream_session_message(
                session_id=session_id,
                message=message,
                user_id=user_id or 'sdk_user',
                metadata=metadata
            ):
                yield chunk
            
            logger.debug(f"Streamed message to session {session_id} for agent {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to stream message to session {session_id}: {str(e)}")
            raise SessionError(f"Failed to stream message: {str(e)}")
    
    def get_session_history(
        self,
        session_id: str,
        limit: int = 50,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a session.
        
        Args:
            session_id: The session ID to get history for
            limit: Maximum number of messages to return
            include_metadata: Whether to include message metadata
            
        Returns:
            List of message dictionaries
            
        Raises:
            SessionError: If history retrieval fails
        """
        try:
            history = self._get_session_history(session_id, limit)
            
            # Process history based on include_metadata flag
            processed_history = []
            for msg in history:
                if 'message_info' in msg:
                    # Extract the actual message content
                    message_data = {
                        'role': msg['message_info'].get('role', 'unknown'),
                        'content': msg['message_info'].get('content', '')
                    }
                    if include_metadata and 'metadata' in msg:
                        message_data['metadata'] = msg['metadata']
                    processed_history.append(message_data)
                else:
                    # Fallback for direct message format
                    message_data = {
                        'role': msg.get('role', 'unknown'),
                        'content': msg.get('content', '')
                    }
                    if include_metadata and 'metadata' in msg:
                        message_data['metadata'] = msg['metadata']
                    processed_history.append(message_data)
            
            logger.debug(f"Retrieved {len(processed_history)} messages from session {session_id}")
            return processed_history
            
        except Exception as e:
            logger.error(f"Failed to get history for session {session_id}: {str(e)}")
            raise SessionError(f"Failed to get session history: {str(e)}")
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an existing session by ID.
        
        Args:
            session_id: The session ID to retrieve
            
        Returns:
            Session instance if found, None otherwise
        """
        # Check cache first
        if session_id in self._session_cache:
            return self._session_cache[session_id]
        
        # Try to create session object from server data
        try:
            session_data = self._get_agent_session(session_id)
            if session_data:
                session = Session(
                    session_id=session_id,
                    agent_client=self,
                    user_id=session_data.get('user_id', 'sdk_user'),
                    metadata=session_data.get('metadata', {})
                )
                self._session_cache[session_id] = session
                return session
        except Exception as e:
            logger.debug(f"Could not retrieve session {session_id}: {str(e)}")
        
        return None
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this agent.
        
        Returns:
            Dictionary containing agent information
            
        Raises:
            NetworkError: If the request fails
        """
        try:
            url = format_url(self.agent_url, "/agent/info")
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API key")
            elif response.status_code == 404:
                raise AgentNotFoundError(f"Agent {self.agent_id} not found")
            elif response.status_code != 200:
                error_data = self._parse_error_response(response)
                raise NetworkError(f"Failed to get agent info: {error_data}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error getting agent info: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of this agent service.
        
        Returns:
            Health status information
            
        Raises:
            NetworkError: If the request fails
        """
        try:
            url = format_url(self.agent_url, "/health")
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code != 200:
                error_data = self._parse_error_response(response)
                raise NetworkError(f"Agent health check failed: {error_data}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error during agent health check: {str(e)}")
    
    
    def _send_session_message(
        self,
        session_id: str,
        message: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Send message to a specific session."""
        try:
            url = format_url(self.agent_url, f"/sessions/{session_id}/messages")
            payload = {
                'message': message,
                'user_id': user_id,
                'stream': False
            }
            
            if metadata:
                payload['metadata'] = metadata
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            self._handle_response_errors(response)
            
            data = response.json()
            return ChatResponse(
                text=data.get('response', ''),
                session_id=session_id,
                token_usage=data.get('token_usage'),
                success=data.get('success', True),
                error=data.get('error'),
                metadata={'agent_id': self.agent_id}
            )
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error sending session message: {str(e)}")
    
    
    def _stream_session_message(
        self,
        session_id: str,
        message: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Iterator[str]:
        """Stream response from session message endpoint."""
        try:
            url = format_url(self.agent_url, f"/sessions/{session_id}/messages")
            payload = {
                'message': message,
                'user_id': user_id,
                'stream': True
            }
            
            if metadata:
                payload['metadata'] = metadata
            
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout,
                stream=True
            )
            
            self._handle_response_errors(response)
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    chunk = clean_json_response(line_text)
                    if chunk and chunk != '[DONE]':
                        yield chunk
                        
        except requests.exceptions.RequestException as e:
            raise StreamingError(f"Network error during streaming: {str(e)}")
    
    def _create_agent_session(
        self,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new session on the agent service."""
        try:
            url = format_url(self.agent_url, "/sessions")
            payload = {'user_id': user_id}
            
            if metadata:
                payload['metadata'] = metadata
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            self._handle_response_errors(response)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error creating session: {str(e)}")
    
    def _get_agent_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from the agent service."""
        try:
            url = format_url(self.agent_url, f"/sessions/{session_id}")
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 404:
                return None
            
            self._handle_response_errors(response)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"Could not fetch session {session_id}: {str(e)}")
            return None
    
    def _get_session_history(
        self, 
        session_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get session message history."""
        try:
            url = format_url(self.agent_url, f"/sessions/{session_id}/messages")
            params = {'limit': limit}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            self._handle_response_errors(response)
            
            data = response.json()
            return data.get('messages', [])
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error getting session history: {str(e)}")
    
    def _get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics."""
        try:
            url = format_url(self.agent_url, f"/sessions/{session_id}/stats")
            response = self.session.get(url, timeout=self.timeout)
            
            self._handle_response_errors(response)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error getting session stats: {str(e)}")
    
    def _handle_response_errors(self, response: requests.Response):
        """Handle common HTTP response errors."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid or expired API key")
        elif response.status_code == 404:
            raise AgentNotFoundError(f"Agent {self.agent_id} not found or endpoint not available")
        elif response.status_code == 429:
            headers = parse_response_headers(dict(response.headers))
            retry_after = headers.get('retry_after', 60)
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=retry_after,
                details=headers
            )
        elif response.status_code >= 400:
            error_data = self._parse_error_response(response)
            raise NetworkError(
                f"HTTP {response.status_code}: {error_data}",
                status_code=response.status_code
            )
    
    def _parse_error_response(self, response: requests.Response) -> str:
        """Parse error message from HTTP response."""
        try:
            data = response.json()
            return extract_error_message(data)
        except (ValueError, KeyError):
            return f"{response.text or 'Unknown error'}"
    
    def close(self):
        """Close the client session."""
        if self.session:
            self.session.close()
        self._session_cache.clear()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        return f"AgentClient(agent_id={self.agent_id}, url={self.agent_url})"
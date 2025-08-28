"""
Alchemist Python SDK - Official Python library for interacting with Alchemist AI agents.

This SDK provides a simple interface to interact with deployed Alchemist agents
using only agent_id and api_key. It handles agent URL resolution, authentication,
session management, and response streaming automatically.

Example:
    >>> from alchemist import AgentClient
    >>> client = AgentClient(agent_id="agent-123", api_key="ak_your_key")
    >>> session = client.create_session()
    >>> response = session.send_message("Hello!")
    >>> print(response.text)
"""

from .client import AgentClient
from .session import Session
from .exceptions import (
    AlchemistError,
    AuthenticationError,
    AgentNotFoundError,
    SessionError,
    RateLimitError,
    NetworkError
)

__version__ = "0.0.1"
__author__ = "Alchemist Team"
__email__ = "support@alchemist.com"

__all__ = [
    "AgentClient", 
    "Session",
    "AlchemistError",
    "AuthenticationError",
    "AgentNotFoundError",
    "SessionError",
    "RateLimitError",
    "NetworkError"
]
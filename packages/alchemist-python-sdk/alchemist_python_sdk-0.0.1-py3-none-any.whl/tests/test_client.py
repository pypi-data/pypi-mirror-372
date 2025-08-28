"""
Basic tests for AgentClient
"""
import pytest
import requests_mock
from alchemist import AgentClient
from alchemist.exceptions import AuthenticationError, AgentNotFoundError


class TestAgentClient:
    def test_client_initialization(self):
        """Test AgentClient initialization with default parameters."""
        client = AgentClient(agent_id="test-agent", api_key="test-key")
        assert client.agent_id == "test-agent"
        assert client.api_key == "test-key"
        assert client.agent_url == "https://agent-test-agent-b3hpe34qdq-uc.a.run.app"
        assert client.timeout == 120

    def test_client_initialization_with_custom_url(self):
        """Test AgentClient initialization with custom URL."""
        custom_url = "https://custom-agent-url.com"
        client = AgentClient(
            agent_id="test-agent", 
            api_key="test-key", 
            agent_url=custom_url
        )
        assert client.agent_url == custom_url

    @requests_mock.Mocker()
    def test_create_session_success(self, m):
        """Test successful session creation."""
        client = AgentClient(agent_id="test-agent", api_key="test-key")
        
        # Mock the session creation endpoint
        m.post(
            f"{client.agent_url}/sessions",
            json={"session_id": "test-session-123"},
            status_code=200
        )
        
        session = client.create_session()
        assert session.session_id == "test-session-123"
        assert session.client == client

    @requests_mock.Mocker()
    def test_create_session_auth_error(self, m):
        """Test session creation with authentication error."""
        client = AgentClient(agent_id="test-agent", api_key="invalid-key")
        
        # Mock authentication error
        m.post(
            f"{client.agent_url}/sessions",
            json={"error": "Invalid API key"},
            status_code=401
        )
        
        with pytest.raises(AuthenticationError):
            client.create_session()

    @requests_mock.Mocker()
    def test_get_session_success(self, m):
        """Test successful session retrieval."""
        client = AgentClient(agent_id="test-agent", api_key="test-key")
        session_id = "existing-session-123"
        
        # Mock the session retrieval endpoint
        m.get(
            f"{client.agent_url}/sessions/{session_id}",
            json={"session_id": session_id, "history": []},
            status_code=200
        )
        
        session = client.get_session(session_id)
        assert session.session_id == session_id
        assert session.client == client

    @requests_mock.Mocker()
    def test_get_session_not_found(self, m):
        """Test session retrieval with session not found."""
        client = AgentClient(agent_id="test-agent", api_key="test-key")
        session_id = "non-existent-session"
        
        # Mock session not found error
        m.get(
            f"{client.agent_url}/sessions/{session_id}",
            json={"error": "Session not found"},
            status_code=404
        )
        
        with pytest.raises(AgentNotFoundError):
            client.get_session(session_id)
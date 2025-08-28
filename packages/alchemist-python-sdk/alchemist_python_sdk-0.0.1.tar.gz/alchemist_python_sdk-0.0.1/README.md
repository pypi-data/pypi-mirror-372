# Alchemist Python SDK

[![PyPI version](https://badge.fury.io/py/alchemist-python-sdk.svg)](https://badge.fury.io/py/alchemist-python-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/alchemist-python-sdk.svg)](https://pypi.org/project/alchemist-python-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for interacting with deployed Alchemist AI agents. This library provides a simple and intuitive interface to integrate Alchemist agents into your Python applications. Each agent has its own API keys, and the service URL is automatically constructed from the agent ID.

## Features

- **Simple Integration**: Just provide `agent_id` and `api_key` - service URLs are auto-constructed
- **Session-First Architecture**: All messages must be sent through sessions for proper conversation context
- **Agent-Specific Authentication**: Each agent has its own API keys with automatic endpoint resolution
- **Session Management**: Persistent conversations with full history and metadata support
- **Streaming Support**: Real-time streaming responses through sessions
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Type Hints**: Full type hint support for better development experience
- **Async Support**: (Coming soon) Async/await pattern support

## Installation

```bash
pip install alchemist-python-sdk
```

### Development Installation

```bash
git clone https://github.com/alchemist/alchemist-python-sdk.git
cd alchemist-python-sdk
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from alchemist import AgentClient

# Initialize the client for a specific agent
# Each agent has its own API key (starts with 'ak_')
# The service URL is automatically constructed from the agent_id
client = AgentClient(
    agent_id="your-agent-id", 
    api_key="ak_your_agent_specific_key"
)

# Step 1: Create a session (required for all messaging)
session = client.create_session(user_id="user123")

# Step 2: Send messages through the session
response = session.send_message("Hello, how can you help me today?")
print(response.text)
```

### Real Example

```python
from alchemist import AgentClient

# Example with real agent ID (replace with your own)
client = AgentClient(
    agent_id="eb77e31c-4bfa-4056-938c-73e690581706",
    api_key="ak_your_actual_api_key_here"
)

# The SDK automatically constructs:
# https://agent-eb77e31c-4bfa-4056-938c-73e690581706-b3hpe34qdq-uc.a.run.app

# Step 1: Create a session first
session = client.create_session(user_id="user123")

# Step 2: Send messages through the session
response = session.send_message("What's the weather like today?")
if response.success:
    print(f"Agent: {response.text}")
else:
    print(f"Error: {response.error}")
```

### Session-Based Conversations

```python
from alchemist import AgentClient

client = AgentClient(
    agent_id="your-agent-id",
    api_key="ak_your_agent_key"
)

# Create a persistent session
session = client.create_session(user_id="user123")

# Have a conversation
response1 = session.send_message("What's the weather like?")
print(f"Agent: {response1.text}")

response2 = session.send_message("What about tomorrow?")
print(f"Agent: {response2.text}")

# Get conversation history
history = session.get_history(include_metadata=False)
for message in history:
    print(f"{message['role']}: {message['content']}")
```

### Streaming Responses

```python
from alchemist import AgentClient

client = AgentClient(
    agent_id="your-agent-id",
    api_key="ak_your_agent_key"
)

# Step 1: Create a session first
session = client.create_session(user_id="user123")

# Step 2: Stream the response in real-time through the session
print("Agent: ", end="", flush=True)
for chunk in session.stream_message("Tell me a long story"):
    print(chunk, end="", flush=True)
print()  # New line after streaming
```

### Multiple Sessions

```python
# You can create multiple sessions for different conversations
session1 = client.create_session(user_id="user123")
session2 = client.create_session(user_id="user456")

# Each session maintains its own conversation history
response1 = session1.send_message("Hello, I'm working on a Python project")
response2 = session2.send_message("Hi, I need help with JavaScript")

# Sessions are independent
print(f"Python conversation: {response1.text}")
print(f"JavaScript conversation: {response2.text}")
```

### Error Handling

```python
from alchemist import AgentClient
from alchemist.exceptions import (
    AuthenticationError,
    AgentNotFoundError,
    RateLimitError,
    NetworkError
)

try:
    client = AgentClient(
        agent_id="your-agent-id",
        api_key="ak_your_agent_key"
    )
    
    # Create session and send message
    session = client.create_session(user_id="user123")
    response = session.send_message("Hello!")
    
except AuthenticationError:
    print("Invalid API key or authentication failed")
except AgentNotFoundError:
    print("Agent not found or not accessible")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except NetworkError as e:
    print(f"Network error: {e}")
```

### Advanced Usage

```python
from alchemist import AgentClient

# Initialize with custom configuration
client = AgentClient(
    agent_id="your-agent-id",
    api_key="ak_your_agent_key",
    timeout=180,  # Custom timeout (default is 120 seconds)
    max_retries=5  # Retry failed requests up to 5 times
)

# Create session with metadata
session = client.create_session(
    user_id="user123",
    metadata={"conversation_type": "support", "priority": "high"}
)

# Send message with metadata through the session
response = session.send_message(
    message="Hello!",
    metadata={"source": "python-sdk", "version": "1.0.0"}
)

# Get agent information
info = client.get_info()
print(f"Agent: {info['name']} - {info['description']}")

# Check agent health
health = client.health_check()
print(f"Agent status: {health['status']}")
```

### Context Manager Usage

```python
from alchemist import AgentClient

# Use as context manager for automatic cleanup
with AgentClient(
    agent_id="your-agent-id", 
    api_key="ak_your_key"
) as client:
    # Create session and send message
    session = client.create_session(user_id="user123")
    response = session.send_message("Hello!")
    print(response.text)
# Client is automatically closed when exiting the context
```

## API Reference

### AgentClient

The main client class for interacting with a specific Alchemist agent.

#### Constructor

```python
AgentClient(
    agent_id: str,
    api_key: str,
    agent_url: Optional[str] = None,
    timeout: int = 120,
    max_retries: int = 3
)
```

- `agent_id`: The unique identifier for the agent (required)
- `api_key`: Agent-specific API key starting with 'ak_' (required)
- `agent_url`: Agent service URL (optional - auto-constructed from agent_id if not provided)
- `timeout`: Request timeout in seconds (default: 120)
- `max_retries`: Maximum retry attempts for failed requests (default: 3)

#### Methods

- `create_session(user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Session`: Create a new session
- `get_session(session_id: str) -> Optional[Session]`: Get an existing session
- `get_info() -> Dict[str, Any]`: Get agent information
- `health_check() -> Dict[str, Any]`: Check agent health

**Note**: All messaging must be done through sessions. The AgentClient does not provide direct chat() or stream() methods.

### Session

Represents a conversation session with an agent.

#### Methods

- `send_message(message: str, stream: bool = False, metadata: Optional[Dict[str, Any]] = None) -> ChatResponse`: Send a message
- `stream_message(message: str, metadata: Optional[Dict[str, Any]] = None) -> Iterator[str]`: Stream a message response
- `get_history(limit: int = 50, include_metadata: bool = True) -> List[Dict[str, Any]]`: Get conversation history
- `get_stats() -> Dict[str, Any]`: Get session statistics
- `clear_history() -> bool`: Clear conversation history

### ChatResponse

Response object from chat interactions.

#### Attributes

- `text: str`: The agent's response text
- `session_id: str`: Session ID for this conversation
- `token_usage: Optional[Dict[str, int]]`: Token usage information
- `metadata: Optional[Dict[str, Any]]`: Response metadata
- `success: bool`: Whether the request was successful
- `error: Optional[str]`: Error message if request failed

### Exceptions

- `AlchemistError`: Base exception class
- `AuthenticationError`: Authentication or API key issues
- `AgentNotFoundError`: Agent not found or not accessible
- `SessionError`: Session-related errors
- `RateLimitError`: Rate limiting errors
- `NetworkError`: Network connectivity issues
- `ValidationError`: Input validation errors
- `StreamingError`: Streaming-related errors

## Architecture

### Session-First Design

**Important**: This SDK enforces a session-first architecture. You cannot send messages directly to agents - all messages must be sent through sessions.

**Required Pattern:**
```python
# ✅ Correct - Always create session first
client = AgentClient(agent_id="...", api_key="...")
session = client.create_session(user_id="user123")
response = session.send_message("Hello!")

# ❌ Incorrect - No direct chat methods available
# client.chat("Hello!")  # This method does not exist
```

**Benefits of Session-First Architecture:**
- **Conversation Context**: Every message has proper conversation history
- **User Management**: Sessions track user IDs and metadata
- **History Access**: Full conversation history and statistics
- **Streaming Support**: Persistent streaming within conversations
- **Metadata Support**: Rich metadata attached to sessions and messages

## How It Works

### Automatic URL Construction

The SDK automatically constructs the agent service URL from your `agent_id` using the pattern:
```
https://agent-{agent_id}-b3hpe34qdq-uc.a.run.app
```

**Example:**
- Agent ID: `eb77e31c-4bfa-4056-938c-73e690581706`  
- Constructed URL: `https://agent-eb77e31c-4bfa-4056-938c-73e690581706-b3hpe34qdq-uc.a.run.app`

This means you only need to provide your `agent_id` and `api_key` - no manual URL configuration required!

### Timeout Configuration

The SDK uses a **120-second default timeout** to accommodate agent processing times. You can customize this:

```python
# For quick responses
client = AgentClient(
    agent_id="your-agent-id",
    api_key="ak_your_agent_key",
    timeout=60  # 60 seconds
)

# For complex processing
client = AgentClient(
    agent_id="your-agent-id", 
    api_key="ak_your_agent_key",
    timeout=300  # 5 minutes
)
```

### Custom Agent URLs (Optional)

If you need to use a custom agent URL (for testing or special deployments), you can override the automatic construction:

```python
client = AgentClient(
    agent_id="your-agent-id",
    api_key="ak_your_agent_key",
    agent_url="https://your-custom-agent-url.com"  # Optional override
)
```

## Configuration

### Environment Variables

You can set default configuration using environment variables:

```bash
export ALCHEMIST_API_KEY="ak_your_agent_specific_key"
export ALCHEMIST_AGENT_ID="your-agent-id"
export ALCHEMIST_TIMEOUT="60"
export ALCHEMIST_MAX_RETRIES="5"
```

### Logging

The SDK uses Python's built-in logging. Enable debug logging to see detailed request/response information:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/alchemist/alchemist-python-sdk.git
cd alchemist-python-sdk
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black alchemist/
flake8 alchemist/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://docs.alchemist.com/python-sdk](https://docs.alchemist.com/python-sdk)
- **Issues**: [GitHub Issues](https://github.com/alchemist/alchemist-python-sdk/issues)
- **Support**: [support@alchemist.com](mailto:support@alchemist.com)

## Changelog

### v2.0.0 (2024-08-27)

- **🔄 BREAKING CHANGE**: Enforced session-first architecture - removed `client.chat()` and `client.stream()` methods
- **Session-Only Messaging**: All messages must be sent through sessions for proper conversation context
- **Automatic URL Construction**: No need to provide agent URLs manually - automatically constructed from agent_id
- **Improved Timeout Handling**: Increased default timeout to 120 seconds for better agent processing support
- **Enhanced History Format**: Fixed conversation history retrieval to work with server response format
- **Simplified API**: Reduced required parameters from 3 to 2 (agent_id and api_key only)
- **Better Error Handling**: Improved timeout and network error management
- **Consistent Architecture**: All messaging flows through sessions for better conversation management

### v1.0.0 (2024-01-XX)

- Initial release
- Basic agent interaction functionality
- Session management
- Streaming response support
- Comprehensive error handling
- Type hint support
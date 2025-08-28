"""
Basic usage examples for the Alchemist Python SDK.

This example demonstrates the fundamental features of the SDK including:
- Client initialization
- Agent interaction
- Basic chat functionality
- Error handling
"""

import os
from alchemist import AgentClient
from alchemist.exceptions import (
    AuthenticationError,
    AgentNotFoundError,
    NetworkError
)


def main():
    """Basic usage example."""
    
    # You can get these values from the Alchemist dashboard
    # Each agent has its own API key (starts with 'ak_')
    api_key = os.getenv("ALCHEMIST_API_KEY", "ak_your-api-key-here")
    agent_id = os.getenv("ALCHEMIST_AGENT_ID", "your-agent-id-here")
    
    if (api_key == "ak_your-api-key-here" or 
        agent_id == "your-agent-id-here"):
        print("Please set ALCHEMIST_API_KEY and ALCHEMIST_AGENT_ID environment variables")
        print("Or update the values in this script")
        print()
        print("Example:")
        print("export ALCHEMIST_API_KEY=ak_agent123_your_key_here")
        print("export ALCHEMIST_AGENT_ID=your-agent-id")  
        print()
        print("💡 You can find these values in the Alchemist dashboard under your agent's settings")
        return
    
    try:
        # Initialize the client for the specific agent
        client = AgentClient(
            agent_id=agent_id,
            api_key=api_key
        )
        print(f"✅ Client initialized for agent {agent_id}")
        print(f"🔗 Agent URL: {client.agent_url}")
        
        # Check agent health
        health = client.health_check()
        print(f"✅ Agent Health: {health.get('status', 'unknown')}")
        
        # Get agent information
        try:
            info = client.get_info()
            print(f"📋 Agent Info: {info.get('name', 'Unknown')} - {info.get('description', 'No description')}")
        except Exception as e:
            print(f"⚠️ Could not fetch agent info: {e}")
        
        # Create a session first (required for all messaging)
        print("\n🔄 Creating session...")
        session = client.create_session(user_id="basic_demo_user")
        print(f"✅ Session created: {session.session_id}")
        
        # Send a simple message through the session
        print("\n💬 Sending message to agent...")
        response = session.send_message("Hello! Can you introduce yourself?")
        
        if response.success:
            print(f"🤖 Agent: {response.text}")
            
            if response.token_usage:
                print(f"📊 Token usage: {response.token_usage}")
        else:
            print(f"❌ Chat failed: {response.error}")
        
        # Send another message through the same session
        print("\n💬 Asking a follow-up question...")
        response2 = session.send_message("What can you help me with?")
        
        if response2.success:
            print(f"🤖 Agent: {response2.text}")
        else:
            print(f"❌ Chat failed: {response2.error}")
        
        # Send message with metadata
        print("\n💬 Sending message with metadata...")
        response3 = session.send_message(
            "Remember my name is John", 
            metadata={"user_name": "John", "source": "basic_usage_example"}
        )
        
        if response3.success:
            print(f"🤖 Agent: {response3.text}")
        else:
            print(f"❌ Chat failed: {response3.error}")
            
    except AuthenticationError:
        print("❌ Authentication failed. Please check your API key.")
    except AgentNotFoundError:
        print("❌ Agent not found. Please check your agent ID.")
    except NetworkError as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    finally:
        # Clean up
        if 'client' in locals():
            client.close()
            print("🧹 Client closed")


if __name__ == "__main__":
    main()
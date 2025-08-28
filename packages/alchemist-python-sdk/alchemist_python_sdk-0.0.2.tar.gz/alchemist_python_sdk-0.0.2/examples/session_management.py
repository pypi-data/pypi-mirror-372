"""
Session management example for the Alchemist Python SDK.

This example demonstrates:
- Creating and managing sessions
- Persistent conversations
- Session history retrieval
- Session statistics
"""

import os
import time
from alchemist import AgentClient
from alchemist.exceptions import (
    AlchemistError,
    SessionError
)


def main():
    """Session management example."""
    
    api_key = os.getenv("ALCHEMIST_API_KEY", "ak_your-api-key-here")
    agent_id = os.getenv("ALCHEMIST_AGENT_ID", "your-agent-id-here")
    
    if (api_key == "ak_your-api-key-here" or 
        agent_id == "your-agent-id-here"):
        print("Please set ALCHEMIST_API_KEY and ALCHEMIST_AGENT_ID environment variables")
        print("Example: export ALCHEMIST_API_KEY=ak_agent123_your_key")
        print("Example: export ALCHEMIST_AGENT_ID=your-agent-id")
        return
    
    try:
        # Initialize client for the specific agent
        client = AgentClient(
            agent_id=agent_id,
            api_key=api_key
        )
        print(f"✅ Connected to agent {agent_id}")
        
        # Create a new session
        print("\n🔄 Creating new session...")
        session = client.create_session(
            user_id="demo_user_123",
            metadata={
                "conversation_type": "demo",
                "created_from": "python_sdk_example",
                "timestamp": time.time()
            }
        )
        
        print(f"✅ Session created: {session.session_id}")
        print(f"👤 User ID: {session.user_id}")
        
        # Have a multi-turn conversation
        conversation_topics = [
            "Hello! I'm testing session management. Can you remember this conversation?",
            "What did I just tell you about?",
            "Can you help me understand how sessions work?",
            "What's my user ID that I mentioned earlier?"
        ]
        
        print(f"\n💬 Starting conversation with {len(conversation_topics)} messages...")
        
        for i, message in enumerate(conversation_topics, 1):
            print(f"\n[Message {i}/{len(conversation_topics)}]")
            print(f"👤 User: {message}")
            
            # Send message to the session
            response = session.send_message(message, metadata={"message_number": i})
            
            if response.success:
                print(f"🤖 Agent: {response.text}")
                
                # Show token usage if available
                if response.token_usage:
                    tokens = response.token_usage.get('total_tokens', 0)
                    print(f"📊 Tokens used: {tokens}")
            else:
                print(f"❌ Message failed: {response.error}")
            
            # Small delay between messages
            time.sleep(1)
        
        # Get conversation history
        print(f"\n📜 Retrieving conversation history...")
        history = session.get_history(include_metadata=True)
        
        print(f"📊 Found {len(history)} messages in history:")
        for msg in history:
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"  {role_icon} {msg['role']}: {content_preview}")
        
        # Get session statistics
        print(f"\n📈 Session statistics:")
        try:
            stats = session.get_stats()
            for key, value in stats.items():
                if key == 'session_id':
                    continue
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"  ⚠️ Could not retrieve stats: {e}")
        
        # Demonstrate session retrieval
        print(f"\n🔍 Testing session retrieval...")
        session_id = session.session_id
        
        # Get the same session by ID
        retrieved_session = client.get_session(session_id)
        
        if retrieved_session:
            print(f"✅ Successfully retrieved session: {retrieved_session.session_id}")
            
            # Send another message to verify it's the same session
            response = retrieved_session.send_message("Do you remember our previous conversation?")
            
            if response.success:
                print(f"🤖 Agent: {response.text}")
            else:
                print(f"❌ Message failed: {response.error}")
        else:
            print("❌ Could not retrieve session")
        
        # Create another session to show multiple sessions
        print(f"\n🔄 Creating second session...")
        session2 = client.create_session(
            user_id="demo_user_456",
            metadata={"conversation_type": "second_demo"}
        )
        
        print(f"✅ Second session created: {session2.session_id}")
        
        # Send a message to the new session
        response = session2.send_message("Hello! This is a new session.")
        if response.success:
            print(f"🤖 Agent (Session 2): {response.text}")
        
        # Show that sessions are independent
        response = session2.send_message("Do you remember talking to demo_user_123?")
        if response.success:
            print(f"🤖 Agent (Session 2): {response.text}")
            print("💡 Notice how the agent treats this as a separate conversation")
        
        # Clean up (optional - demonstrates history clearing)
        print(f"\n🧹 Cleaning up session history...")
        if session.clear_history():
            print("✅ Session 1 history cleared")
        
        if session2.clear_history():
            print("✅ Session 2 history cleared")
            
    except SessionError as e:
        print(f"❌ Session error: {e}")
    except AlchemistError as e:
        print(f"❌ Alchemist error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    finally:
        if 'client' in locals():
            client.close()
            print("🧹 Client closed")


if __name__ == "__main__":
    main()
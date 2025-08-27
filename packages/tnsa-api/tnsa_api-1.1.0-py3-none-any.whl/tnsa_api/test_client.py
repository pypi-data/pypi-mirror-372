#!/usr/bin/env python3
"""
Test script for TNSA API client.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import from current directory
from client import TNSA
from async_client import AsyncTNSA
from exceptions import TNSAError


def test_sync_client():
    """Test synchronous client."""
    print("Testing synchronous client...")
    
    try:
        # Initialize client with config file
        client = TNSA(
            api_key="test-key",
            base_url="https://api.tnsaai.com"
        )
        
        print(f"✓ Client initialized successfully")
        print(f"  Base URL: {client.config.base_url}")
        print(f"  Timeout: {client.config.timeout}")
        print(f"  Max retries: {client.config.max_retries}")
        
        # Test model listing (this will fail without valid API key, but tests the structure)
        try:
            models = client.models.list()
            print(f"✓ Models interface works: {len(models)} models available")
        except TNSAError as e:
            print(f"⚠ Models request failed (expected without valid API key): {e}")
        
        # Test chat interface structure
        try:
            response = client.chat.completions.create(
                model="NGen3.9-Pro",
                messages=[{"role": "user", "content": "Hello!"}]
            )
            print(f"✓ Chat completion successful")
        except TNSAError as e:
            print(f"⚠ Chat request failed (expected without valid API key): {e}")
        
        # Test conversation management
        conversation = client.conversations.create(
            model="NGen3.9-Pro",
            system_prompt="You are a helpful assistant."
        )
        print(f"✓ Conversation created: {conversation.id}")
        
        conversations = client.conversations.list()
        print(f"✓ Conversations listed: {len(conversations)} conversations")
        
        client.close()
        print("✓ Sync client test completed")
        
    except Exception as e:
        print(f"✗ Sync client test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_async_client():
    """Test asynchronous client."""
    print("\nTesting asynchronous client...")
    
    try:
        async with AsyncTNSA(
            api_key="test-key",
            base_url="https://api.tnsaai.com"
        ) as client:
            
            print(f"✓ Async client initialized successfully")
            print(f"  Base URL: {client.config.base_url}")
            
            # Test model listing
            try:
                models = await client.models.list()
                print(f"✓ Async models interface works: {len(models)} models available")
            except TNSAError as e:
                print(f"⚠ Async models request failed (expected without valid API key): {e}")
            
            # Test chat interface
            try:
                response = await client.chat.completions.create(
                    model="NGen3.9-Lite",
                    messages=[{"role": "user", "content": "Hello async!"}]
                )
                print(f"✓ Async chat completion successful")
            except TNSAError as e:
                print(f"⚠ Async chat request failed (expected without valid API key): {e}")
            
            # Test conversation management
            conversation = await client.conversations.create(
                model="NGen3.9-Lite",
                system_prompt="You are an async assistant."
            )
            print(f"✓ Async conversation created: {conversation.id}")
            
            conversations = await client.conversations.list()
            print(f"✓ Async conversations listed: {len(conversations)} conversations")
        
        print("✓ Async client test completed")
        
    except Exception as e:
        print(f"✗ Async client test failed: {e}")
        import traceback
        traceback.print_exc()


def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration loading...")
    
    try:
        # Test environment variable loading
        os.environ["TNSA_API_KEY"] = "env-test-key"
        os.environ["TNSA_BASE_URL"] = "https://env.tnsaai.com"
        os.environ["TNSA_TIMEOUT"] = "45.0"
        
        client = TNSA()
        
        assert client.config.api_key == "env-test-key"
        assert client.config.base_url == "https://env.tnsaai.com"
        assert client.config.timeout == 45.0
        
        print("✓ Environment variable configuration works")
        
        # Test parameter override
        client2 = TNSA(
            api_key="param-key",
            base_url="https://param.tnsaai.com",
            timeout=60.0
        )
        
        assert client2.config.api_key == "param-key"
        assert client2.config.base_url == "https://param.tnsaai.com"
        assert client2.config.timeout == 60.0
        
        print("✓ Parameter override configuration works")
        
        # Clean up environment
        del os.environ["TNSA_API_KEY"]
        del os.environ["TNSA_BASE_URL"]
        del os.environ["TNSA_TIMEOUT"]
        
        client.close()
        client2.close()
        
        print("✓ Configuration test completed")
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()


def test_data_models():
    """Test data model functionality."""
    print("\nTesting data models...")
    
    try:
        from models.chat import ChatMessage, ChatCompletion
        from models.common import Usage, Model
        
        # Test ChatMessage
        message = ChatMessage(role="user", content="Hello world!")
        assert message.role == "user"
        assert message.content == "Hello world!"
        
        message_dict = message.to_dict()
        message2 = ChatMessage.from_dict(message_dict)
        assert message2.role == message.role
        assert message2.content == message.content
        
        print("✓ ChatMessage model works")
        
        # Test Usage
        usage = Usage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
            estimated_cost=0.05
        )
        assert usage.total_tokens == 30
        
        print("✓ Usage model works")
        
        # Test Model
        model = Model(
            id="NGen3.9-Pro",
            capabilities=["chat", "completion"]
        )
        assert model.supports_capability("chat")
        assert not model.supports_capability("vision")
        
        print("✓ Model class works")
        
        print("✓ Data models test completed")
        
    except Exception as e:
        print(f"✗ Data models test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("TNSA API Client Test Suite")
    print("=" * 50)
    
    test_config_loading()
    test_data_models()
    test_sync_client()
    
    # Run async test
    asyncio.run(test_async_client())
    
    print("\n" + "=" * 50)
    print("Test suite completed!")


if __name__ == "__main__":
    main()
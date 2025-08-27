#!/usr/bin/env python3
"""
Demo script showing TNSA API client usage with the current backend.
"""

import os
import sys
import asyncio
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules directly
from config import Config
from client import TNSA
from async_client import AsyncTNSA
from exceptions import TNSAError


def demo_sync_client():
    """Demonstrate synchronous client usage."""
    print("=== Synchronous Client Demo ===")
    
    try:
        # Initialize client with local backend
        client = TNSA(
            api_key="demo-key",  # The backend doesn't validate this for most models
            base_url="http://localhost:8000"  # Local backend
        )
        
        print(f"✓ Client initialized")
        print(f"  Base URL: {client.config.base_url}")
        print(f"  Timeout: {client.config.timeout}s")
        
        # Test model listing
        print("\n1. Listing available models...")
        try:
            models = client.models.list()
            print(f"✓ Found {len(models)} models:")
            for model in models:
                print(f"  - {model.id} (context: {model.context_length}, capabilities: {model.capabilities})")
        except Exception as e:
            print(f"⚠ Model listing failed: {e}")
        
        # Test chat completion with NGen3.9-Lite
        print("\n2. Testing chat completion with NGen3.9-Lite...")
        try:
            response = client.chat.create(
                model="NGen3.9-Lite",
                messages=[
                    {"role": "user", "content": "Hello! Please introduce yourself briefly."}
                ],
                temperature=0.7
            )
            
            print(f"✓ Chat completion successful!")
            print(f"  Response: {response.choices[0].message.content[:200]}...")
            if response.usage:
                print(f"  Usage: {response.usage.total_tokens} tokens, ${response.usage.estimated_cost:.4f}")
            
        except Exception as e:
            print(f"⚠ Chat completion failed: {e}")
        
        # Test streaming
        print("\n3. Testing streaming response...")
        try:
            stream = client.chat.create(
                model="NGen3.9-Lite",
                messages=[
                    {"role": "user", "content": "Count from 1 to 5, one number per line."}
                ],
                stream=True
            )
            
            print("✓ Streaming response:")
            full_response = ""
            for chunk in stream:
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                    full_response += chunk.content
            
            print(f"\n  Full response length: {len(full_response)} characters")
            
            # Get streaming stats if available
            if hasattr(stream, 'stats') and stream.stats:
                stats = stream.stats
                print(f"  Stats: {stats.total_tokens} tokens, ${stats.estimated_cost:.4f}")
            
        except Exception as e:
            print(f"⚠ Streaming failed: {e}")
        
        # Test conversation management
        print("\n4. Testing conversation management...")
        try:
            conversation = client.conversations.create(
                model="NGen3.9-Lite",
                system_prompt="You are a helpful coding assistant."
            )
            print(f"✓ Created conversation: {conversation.id}")
            
            conversations = client.conversations.list()
            print(f"✓ Listed {len(conversations)} conversations")
            
        except Exception as e:
            print(f"⚠ Conversation management failed: {e}")
        
        client.close()
        print("\n✓ Sync demo completed")
        
    except Exception as e:
        print(f"✗ Sync demo failed: {e}")
        import traceback
        traceback.print_exc()


async def demo_async_client():
    """Demonstrate asynchronous client usage."""
    print("\n=== Asynchronous Client Demo ===")
    
    try:
        async with AsyncTNSA(
            api_key="demo-key",
            base_url="http://localhost:8000"
        ) as client:
            
            print(f"✓ Async client initialized")
            
            # Test async model listing
            print("\n1. Async model listing...")
            try:
                models = await client.models.list()
                print(f"✓ Found {len(models)} models asynchronously")
            except Exception as e:
                print(f"⚠ Async model listing failed: {e}")
            
            # Test async chat completion
            print("\n2. Async chat completion...")
            try:
                response = await client.chat.create(
                    model="NGen3.9-Lite",
                    messages=[
                        {"role": "user", "content": "What's 2+2? Answer briefly."}
                    ]
                )
                
                print(f"✓ Async chat completion successful!")
                print(f"  Response: {response.choices[0].message.content}")
                
            except Exception as e:
                print(f"⚠ Async chat completion failed: {e}")
            
            # Test async streaming
            print("\n3. Async streaming...")
            try:
                stream = await client.chat.create(
                    model="NGen3.9-Lite",
                    messages=[
                        {"role": "user", "content": "Say hello in 3 different languages."}
                    ],
                    stream=True
                )
                
                print("✓ Async streaming response:")
                async for chunk in stream:
                    if chunk.content:
                        print(chunk.content, end="", flush=True)
                print()
                
            except Exception as e:
                print(f"⚠ Async streaming failed: {e}")
        
        print("\n✓ Async demo completed")
        
    except Exception as e:
        print(f"✗ Async demo failed: {e}")
        import traceback
        traceback.print_exc()


def demo_farmvaidya():
    """Demonstrate Farmvaidya-Bot usage."""
    print("\n=== Farmvaidya-Bot Demo ===")
    
    try:
        # Farmvaidya requires specific token
        client = TNSA(
            api_key="d00ce3dd2481f07cd2145e6099a6e0d301142ef46f646a2a0f520f04699afafc",  # Farmvaidya token
            base_url="http://localhost:8000"
        )
        
        print("✓ Farmvaidya client initialized")
        
        # Test agricultural query
        print("\n1. Testing agricultural query...")
        try:
            response = client.chat.create(
                model="Farmvaidya-Bot",
                messages=[
                    {"role": "user", "content": "What are the best practices for coconut farming irrigation?"}
                ]
            )
            
            print(f"✓ Farmvaidya response:")
            print(f"  {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"⚠ Farmvaidya query failed: {e}")
        
        # Test non-agricultural query (should be rejected)
        print("\n2. Testing non-agricultural query...")
        try:
            response = client.chat.create(
                model="Farmvaidya-Bot",
                messages=[
                    {"role": "user", "content": "What's the weather like today?"}
                ]
            )
            
            print(f"✓ Non-agricultural response:")
            print(f"  {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"⚠ Non-agricultural query failed: {e}")
        
        client.close()
        print("\n✓ Farmvaidya demo completed")
        
    except Exception as e:
        print(f"✗ Farmvaidya demo failed: {e}")


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n=== Error Handling Demo ===")
    
    try:
        # Test with invalid API key
        client = TNSA(
            api_key="invalid-key",
            base_url="http://localhost:8000"
        )
        
        print("1. Testing invalid model...")
        try:
            response = client.chat.create(
                model="NonExistentModel",
                messages=[{"role": "user", "content": "Hello"}]
            )
        except TNSAError as e:
            print(f"✓ Caught expected error: {e}")
        
        print("\n2. Testing connection error...")
        client_bad_url = TNSA(
            api_key="test-key",
            base_url="http://localhost:9999"  # Non-existent server
        )
        
        try:
            models = client_bad_url.models.list()
        except TNSAError as e:
            print(f"✓ Caught connection error: {e}")
        
        client.close()
        client_bad_url.close()
        print("\n✓ Error handling demo completed")
        
    except Exception as e:
        print(f"✗ Error handling demo failed: {e}")


def main():
    """Run all demos."""
    print("TNSA API Client Demo")
    print("=" * 50)
    print("This demo connects to the local TNSA backend at http://localhost:8000")
    print("Make sure the backend server is running before proceeding.")
    print("=" * 50)
    
    # Check if backend is running
    try:
        import requests
        response = requests.get("http://localhost:8000/models", timeout=5)
        print(f"✓ Backend is running (status: {response.status_code})")
    except Exception as e:
        print(f"⚠ Backend check failed: {e}")
        print("  Make sure to start the backend server first!")
        print("  Run: python backend/main.py")
        return
    
    # Run demos
    demo_sync_client()
    asyncio.run(demo_async_client())
    demo_farmvaidya()
    demo_error_handling()
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("\nNext steps:")
    print("1. Install the package: python install_package.py")
    print("2. Use in your projects: from tnsa_api_v2 import TNSA")
    print("3. Check example.py for more usage patterns")


if __name__ == "__main__":
    main()
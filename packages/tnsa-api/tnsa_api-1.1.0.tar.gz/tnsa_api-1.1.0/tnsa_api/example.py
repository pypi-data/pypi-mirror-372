#!/usr/bin/env python3
"""
Example usage of TNSA API client.
"""

import os
import sys
import asyncio

# For development - add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def sync_example():
    """Example using synchronous client."""
    print("=== Synchronous Client Example ===")
    
    # You can set your API key as an environment variable
    # os.environ["TNSA_API_KEY"] = "your-api-key-here"
    
    from tnsa_api_v2 import TNSA
    
    # Initialize client
    client = TNSA(
        api_key="your-api-key-here",  # Replace with your actual API key
        base_url="https://api.tnsaai.com"  # This will be the actual endpoint
    )
    
    try:
        # List available models
        print("Listing available models...")
        models = client.models.list()
        print(f"Available models: {[model.id for model in models]}")
        
        # Create a chat completion
        print("\nCreating chat completion...")
        response = client.chat.completions.create(
            model="NGen3.9-Pro",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! How are you today?"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage.total_tokens} tokens, ${response.usage.estimated_cost:.4f}")
        
        # Streaming example
        print("\nStreaming example...")
        stream = client.chat.completions.create(
            model="NGen3.9-Lite",
            messages=[{"role": "user", "content": "Tell me a short joke"}],
            stream=True
        )
        
        print("Streaming response: ", end="")
        for chunk in stream:
            if chunk.content:
                print(chunk.content, end="", flush=True)
        print()  # New line after streaming
        
        # Conversation management
        print("\nConversation management...")
        conversation = client.conversations.create(
            model="NGen3.9-Pro",
            system_prompt="You are a coding assistant."
        )
        print(f"Created conversation: {conversation.id}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This example requires a valid API key and running TNSA API server.")
    
    finally:
        client.close()


async def async_example():
    """Example using asynchronous client."""
    print("\n=== Asynchronous Client Example ===")
    
    from tnsa_api_v2 import AsyncTNSA
    
    async with AsyncTNSA(
        api_key="your-api-key-here",  # Replace with your actual API key
        base_url="https://api.tnsaai.com"
    ) as client:
        
        try:
            # List models asynchronously
            print("Listing models asynchronously...")
            models = await client.models.list()
            print(f"Available models: {[model.id for model in models]}")
            
            # Create async chat completion
            print("\nCreating async chat completion...")
            response = await client.chat.completions.create(
                model="NGen3.9-Lite",
                messages=[
                    {"role": "user", "content": "What's the weather like in async world?"}
                ]
            )
            
            print(f"Async response: {response.choices[0].message.content}")
            
            # Async streaming
            print("\nAsync streaming example...")
            stream = await client.chat.completions.create(
                model="NGen3.9-Lite",
                messages=[{"role": "user", "content": "Count from 1 to 5"}],
                stream=True
            )
            
            print("Async streaming: ", end="")
            async for chunk in stream:
                if chunk.content:
                    print(chunk.content, end="", flush=True)
            print()
            
        except Exception as e:
            print(f"Async error: {e}")
            print("Note: This example requires a valid API key and running TNSA API server.")


def configuration_example():
    """Example of different configuration methods."""
    print("\n=== Configuration Examples ===")
    
    from tnsa_api_v2 import TNSA
    
    # Method 1: Direct parameters
    print("1. Direct parameters:")
    client1 = TNSA(
        api_key="direct-api-key",
        base_url="https://api.tnsaai.com",
        timeout=30.0,
        max_retries=3
    )
    print(f"   Base URL: {client1.config.base_url}")
    print(f"   Timeout: {client1.config.timeout}")
    client1.close()
    
    # Method 2: Environment variables
    print("\n2. Environment variables:")
    os.environ["TNSA_API_KEY"] = "env-api-key"
    os.environ["TNSA_BASE_URL"] = "https://env.tnsaai.com"
    os.environ["TNSA_TIMEOUT"] = "45.0"
    
    client2 = TNSA()
    print(f"   Base URL: {client2.config.base_url}")
    print(f"   Timeout: {client2.config.timeout}")
    client2.close()
    
    # Clean up environment variables
    del os.environ["TNSA_API_KEY"]
    del os.environ["TNSA_BASE_URL"]
    del os.environ["TNSA_TIMEOUT"]
    
    # Method 3: Configuration file (would load from config.yaml)
    print("\n3. Configuration file:")
    print("   Create a config.yaml file with your settings")
    print("   The client will automatically find and load it")


def model_specific_examples():
    """Examples for different TNSA models."""
    print("\n=== Model-Specific Examples ===")
    
    from tnsa_api_v2 import TNSA
    
    client = TNSA(api_key="your-api-key", base_url="https://api.tnsaai.com")
    
    try:
        # NGen3.9-Pro - High performance model
        print("1. NGen3.9-Pro (High Performance):")
        print("   Best for: Complex reasoning, long conversations, detailed analysis")
        
        # NGen3.9-Lite - Fast and efficient
        print("\n2. NGen3.9-Lite (Fast & Efficient):")
        print("   Best for: Quick responses, simple tasks, high throughput")
        
        # Farmvaidya-Bot - Agricultural specialist
        print("\n3. Farmvaidya-Bot (Agricultural Specialist):")
        print("   Best for: Farming advice, agricultural questions, crop management")
        
        # Example with Farmvaidya-Bot
        farmvaidya_response = client.chat.completions.create(
            model="Farmvaidya-Bot",
            messages=[
                {"role": "user", "content": "What are the best practices for coconut farming?"}
            ]
        )
        print(f"   Example response: {farmvaidya_response.choices[0].message.content[:100]}...")
        
    except Exception as e:
        print(f"Model examples error: {e}")
    
    finally:
        client.close()


def main():
    """Run all examples."""
    print("TNSA API Client Examples")
    print("=" * 50)
    print("Note: Replace 'your-api-key-here' with your actual API key")
    print("=" * 50)
    
    # Configuration examples (these work without API key)
    configuration_example()
    
    # Model information (these work without API key)
    model_specific_examples()
    
    # Uncomment these to test with actual API key:
    # sync_example()
    # asyncio.run(async_example())
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo use with real API:")
    print("1. Get your API key from TNSA")
    print("2. Replace 'your-api-key-here' with your actual key")
    print("3. Ensure the TNSA API server is running")
    print("4. Uncomment the sync_example() and async_example() calls")


if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""Test LLM connection (Task 33)"""

from testgen.core.llm import LLMClient
from testgen.config import config

def test_connection():
    print("=" * 70)
    print("TESTING LLM CONNECTION (Task 33)")
    print("=" * 70)
    print()
    
    # Show configuration
    print("Configuration:")
    print(f"  Provider: {config.llm_provider.value}")
    print(f"  Model: {config.llm_model}")
    print(f"  Temperature: {config.llm_temperature}")
    print(f"  Has API Key: {config.get_api_key() is not None}")
    print()
    
    # Create client
    print("Creating LLM client...")
    try:
        client = LLMClient()
        print("✅ Client created successfully!")
        print()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return
    
    # Show model info
    info = client.get_model_info()
    print("Model Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()
    
    # Test connection
    print("Testing connection...")
    try:
        is_connected = client.test_connection()
        if is_connected:
            print("✅ Connection test passed!")
        else:
            print("❌ Connection test failed")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # Simple generation test
    print("Testing generation...")
    try:
        response = client.generate(
            prompt="Write a simple Python function that adds two numbers. Just the code, no explanation.",
            max_tokens=200
        )
        
        print("✅ Generation successful!")
        print()
        print("Response:")
        print("-" * 70)
        print(response.content)
        print("-" * 70)
        print()
        
        print("Metadata:")
        print(f"  Model: {response.model}")
        print(f"  Provider: {response.provider}")
        print(f"  Tokens used: {response.tokens_used}")
        print(f"    Input: {response.input_tokens}")
        print(f"    Output: {response.output_tokens}")
        print(f"  Estimated cost: ${response.cost:.6f}")
        print()
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return
    
    print("=" * 70)
    print("✅ ALL TESTS PASSED - LLM CLIENT READY!")
    print("=" * 70)

if __name__ == "__main__":
    test_connection()

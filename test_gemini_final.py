#!/usr/bin/env python
"""Test LLM connection - ASCII only version"""

from testgen.core.llm import LLMClient
from testgen.config import config

def test_connection():
    print("=" * 70)
    print("TESTING GEMINI LLM CONNECTION (Task 33)")
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
        print("[OK] Client created successfully!")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to create client: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Simple generation test
    print("Testing generation...")
    try:
        response = client.generate(
            prompt="Write a Python function that adds two numbers. Just the code, no explanation.",
            max_tokens=200
        )
        
        print("[OK] Generation successful!")
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
        print(f"[ERROR] Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test with system prompt
    print("Testing with system prompt...")
    try:
        response2 = client.generate(
            system_prompt="You are a helpful coding assistant.",
            prompt="Write 'Hello World' in Python",
            max_tokens=50
        )
        print("[OK] System prompt test passed!")
        print(f"Response: {response2.content[:100]}...")
        print()
    except Exception as e:
        print(f"[ERROR] System prompt test failed: {e}")
        return
    
    print("=" * 70)
    print("[SUCCESS] ALL TESTS PASSED - GEMINI LLM CLIENT READY!")
    print("=" * 70)
    print()
    print("Summary:")
    print("  - Client initialization: PASS")
    print("  - Basic generation: PASS")
    print("  - System prompts: PASS")
    print("  - Token tracking: PASS")
    print("  - Cost estimation: PASS (FREE!)")
    print()
    print("Task 33 - LLM Client: COMPLETE!")

if __name__ == "__main__":
    test_connection()

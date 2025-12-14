#!/usr/bin/env python
"""Simple demo of test generation (Task 36)"""

from testgen.core.llm import LLMClient
from testgen.core.prompt_generator import TestPromptGenerator
from testgen.core.scanner import CodeScanner

def main():
    print("=" * 70)
    print("TASK 36: TEST GENERATION DEMO")
    print("=" * 70)
    print()
    
    # Scan actual code
    print("Scanning code...")
    scanner = CodeScanner()
    result = scanner.scan_directory("tests/fixtures/python_project")
    
    if not result.files:
        print("No files found!")
        return
    
    # Take first file
    code_file = result.files[0]
    print(f"File: {code_file.relative_path}")
    print(f"Lines: {code_file.line_count}")
    print()
    
    # Generate prompt
    print("Generating prompt...")
    generator = TestPromptGenerator(include_examples=False)
    system_prompt = generator.get_system_prompt()
    user_prompt = generator.generate_for_file(code_file)
    
    print(f"System prompt: {len(system_prompt)} chars")
    print(f"User prompt: {len(user_prompt)} chars")
    print()
    
    # Generate tests
    print("Generating tests with LLM...")
    client = LLMClient()
    
    response = client.generate(
        system_prompt=system_prompt,
        prompt=user_prompt,
        max_tokens=1500
    )
    
    print()
    print("=" * 70)
    print("GENERATED TESTS:")
    print("=" * 70)
    print(response.content[:1000])
    if len(response.content) > 1000:
        print("...")
        print(f"(Total: {len(response.content)} chars)")
    print("=" * 70)
    print()
    print(f"Tokens: {response.tokens_used}, Cost: ${response.cost:.4f}")
    print()
    print("[SUCCESS] Task 36 Complete!")

if __name__ == "__main__":
    main()

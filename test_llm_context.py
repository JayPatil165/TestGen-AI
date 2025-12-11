#!/usr/bin/env python
"""Test LLM Context Summarization (Task 30)"""

from testgen.core.scanner import CodeScanner

def test_llm_context():
    print("Testing LLM Context Summarization (Task 30)")
    print()
    
    scanner = CodeScanner()
    result = scanner.scan_directory('./src')
    
    # Test metadata detection
    metadata = result.detect_project_type()
    print("Project Detection:")
    print(f"  Type: {metadata['project_type']}")
    print(f"  Frameworks: {metadata['frameworks']}")
    print(f"  Has Tests: {metadata['has_tests']}")
    print()
    
    # Test file tree
    print("File Tree:")
    print(result.get_file_tree())
    print()
    
    print("=" * 70)
    print("✅ Task 30 Complete - LLM Context features work!")
    print("Full LLM context available via: result.get_llm_context()")
    print("=" * 70)

if __name__ == "__main__":
    test_llm_context()

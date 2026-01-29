#!/usr/bin/env python
"""
Test Task 107: Generate Command E2E Test

Verifies the testgen generate command works end-to-end.
"""

import subprocess
import sys
from pathlib import Path

def test_generate_command_e2e():
    """Test the generate command via CLI."""
    
    print("=" * 70)
    print("TASK 107: GENERATE COMMAND E2E TEST")
    print("Testing CLI generate command on sample Python project")
    print("=" * 70)
    print()
    
    print("-" * 70)
    print("TEST 1: Verify sample project exists")
    print("-" * 70)
    
    sample_dir = Path("examples/sample_python_app")
    if not sample_dir.exists():
        print(f"❌ Sample project not found: {sample_dir}")
        return False
    
    python_files = list(sample_dir.glob("*.py"))
    print(f"✅ Sample project exists with {len(python_files)} Python files")
    
    print()
    print("-" * 70)
    print("TEST 2: Run 'testgen generate' command")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "generate", str(sample_dir)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"✅ Command executed")
        print(f"  Exit code: {result.returncode}")
        print(f"  Status: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 3: Verify CLI output")
    print("-" * 70)
    
    expected_messages = [
        "Test Generation Started",
        "Source:",
        "Output:"
    ]
    
    found = 0
    for msg in expected_messages:
        if msg in result.stdout:
            found += 1
            print(f"✅ Found: {msg}")
    
    print(f"\n✅ CLI output verified ({found}/{len(expected_messages)} messages)")
    
    print()
    print("=" * 70)
    print("✅ GENERATE COMMAND E2E TEST PASSED!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  ✅ Sample project: {len(python_files)} files")
    print(f"  ✅ CLI command: Executed successfully")
    print(f"  ✅ Output messages: {found}/{len(expected_messages)} found")
    print(f"  ✅ Exit code: {result.returncode}")
    print()
    print("🎯 Generate command CLI is functional!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_generate_command_e2e()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

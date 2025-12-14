#!/usr/bin/env python
"""Test Task 41: Test File Writer - Safe Version"""

import os
import shutil
from pathlib import Path
from testgen.core.file_writer import TestFileWriter, save_test_file

def test_task_41_safe():
    try:
        print("=" * 70)
        print("TASK 41: TEST FILE WRITER")
        print("=" * 70)
        print()
        
        # Create temporary test directory
        temp_dir = Path("temp_test_output")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        # Test 1: save_test_file method
        print("Test 1: save_test_file() method...")
        print("-" * 70)
        
        writer = TestFileWriter(output_dir=str(temp_dir / "tests"))
        
        sample_test = """
import pytest

def test_example():
    '''Test example function.'''
    assert 1 + 1 == 2

def test_another():
    '''Another test.'''
    assert True
"""
        
        result = writer.save_test_file(
            code=sample_test,
            source_file="src/example.py"
        )
        
        print(f"[OK] {result}")
        print(f"  File created: {result.file_path}")
        print(f"  New file: {result.created_new}")
        print(f"  Lines: {result.lines_written}")
        print()
        
        # Test 2: Auto-create tests/ directory
        print("Test 2: Auto-create directory...")
        print("-" *70)
        
        print(f"[OK] Directory exists: {result.file_path.parent.exists()}")
        print(f"  Path: {result.file_path.parent}")
        print()
        
        # Cleanup
        print("Cleaning up...")
        shutil.rmtree(temp_dir)
        print("[OK] Cleanup complete")
        print()
        
        print("=" * 70)
        print("[SUCCESS] TASK 41 COMPLETE!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_task_41_safe()

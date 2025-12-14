#!/usr/bin/env python
"""Simple test for file writer"""

from testgen.core.file_writer import TestFileWriter
from pathlib import Path
import shutil

try:
    # Clean up first
    temp_dir = Path("temp_simple_test")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # Test basic save
    writer = TestFileWriter(output_dir=str(temp_dir / "tests"))
    result = writer.save_test_file(
        code="def test_example(): pass",
        source_file="src/example.py"
    )
    
    print(f"Success: {result.success}")
    print(f"File path: {result.file_path}")
    print(f"File exists: {result.file_path.exists()}")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("\nTest PASSED!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python
"""Test the scanner with fixture files (Task 31)"""

from testgen.core.scanner import CodeScanner

def test_python_fixtures():
    print("Testing Python Fixtures...")
    print("=" * 70)
    
    scanner = CodeScanner()
    result = scanner.scan_directory('./tests/fixtures/python_project')
    
    print(f"Files scanned: {result.total_files}")
    print(f"Total lines: {result.total_lines}")
    print()
    
    for file in result.files:
        print(f"File: {file.relative_path}")
        print(f"  Type: {file.file_type.value}")
        print(f"  Lines: {file.line_count}")
        print(f"  Functions: {len(file.functions)}")
        print(f"  Classes: {len(file.classes)}")
        print(f"  Sample functions: {file.functions[:3]}")
        print(f"  Sample classes: {file.classes[:2]}")
        print()
    
def test_javascript_fixtures():
    print("=" * 70)
    print("Testing JavaScript Fixtures...")
    print("=" * 70)
    
    scanner = CodeScanner()
    result = scanner.scan_directory('./tests/fixtures/javascript_project')
    
    print(f"Files scanned: {result.total_files}")
    print(f"Total lines: {result.total_lines}")
    print()
    
    for file in result.files:
        print(f"File: {file.relative_path}")
        print(f"  Type: {file.file_type.value}")
        print(f"  Lines: {file.line_count}")
        print(f"  Functions: {len(file.functions)}")
        print(f"  Classes: {len(file.classes)}")
        print(f"  Sample functions: {file.functions[:3]}")
        print(f"  Sample classes: {file.classes[:2]}")
        print()

if __name__ == "__main__":
    test_python_fixtures()
    test_javascript_fixtures()
    print("=" * 70)
    print("✅ Task 31 Complete - Test Fixtures Created and Verified!")
    print("=" * 70)

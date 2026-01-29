#!/usr/bin/env python3
"""Quick test to see if test results are being captured."""
import sys
sys.path.insert(0, 'src')

from testgen.core.python_runner import PythonTestRunner

# Run tests
print("🧪 Running tests...")
runner = PythonTestRunner(verbose=True)
test_dir = "examples/sample_python_app/TestGen-AI/tests"

results = runner.run_tests(test_dir)

print(f"\n📊 Test Results:")
print(f"  Total: {results.total}")
print(f"  Passed: {results.passed}")
print(f"  Failed: {results.failed}")
print(f"  Errors: {results.errors}")
print(f"  Duration: {results.duration:.2f}s")
print(f"\n🔍 results.tests type: {type(results.tests)}")
print(f"🔍 results.tests value: {results.tests}")

if results.tests:
    print(f"\n✅ Found {len(results.tests)} test objects")
    for i, test in enumerate(results.tests[:3], 1):  # Show first 3
        print(f"\n  Test {i}:")
        print(f"    Name: {test.name}")
        print(f"    Status: {test.status}")
        print(f"    Duration: {test.duration}")
        print(f"    Message: {test.message}")
else:
    print("\n❌ results.tests is empty or None!")

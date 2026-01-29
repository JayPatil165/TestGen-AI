#!/usr/bin/env python3
"""Run tests and generate report with actual results."""
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, 'src')

from testgen.ui.reporter import ReportGenerator, ExecutionSummary
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

# Create execution summary
print(f"\n🔍 Debug - results.tests: {results.tests}")
print(f"🔍 Debug - Number of tests: {len(results.tests) if results.tests else 0}")

# Build test results list
test_results_list = []
if results.tests:
    for test in results.tests:
        print(f"  Test: {test.name} - Status: {test.status}")
        test_results_list.append({
            'test_name': test.name,
            'status': test.status.upper(),
            'duration': test.duration,
            'details': test.message or '',
            'language': 'python'
        })

summary = ExecutionSummary(
    project_name="sample_python_app",
    total=results.total,
    passed=results.passed,
    failed=results.failed,
    skipped=results.skipped,
    duration=results.duration,
    language="python",
    results=test_results_list
)

# Generate report
print(f"\n🔍 Debug - summary.results: {summary.results}")
print(f"🔍 Debug - Number of results in summary: {len(summary.results)}")

reporter = ReportGenerator()
output_path = Path("examples/sample_python_app/TestGen-AI/reports/test_report.html")
output_path.parent.mkdir(parents=True, exist_ok=True)

reporter.generate_html(summary, str(output_path))
print(f"\n✅ Report generated: {output_path}")
print(f"📊 Open: file:///{output_path.absolute()}")

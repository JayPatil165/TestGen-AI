#!/usr/bin/env python3
"""
Quick fix for test results table - parse pytest output to get individual test results.
"""
import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, 'src')

from testgen.ui.reporter import ReportGenerator, ExecutionSummary

# Run tests with verbose output
print("🧪 Running tests with verbose output...")
test_dir = "examples/sample_python_app/TestGen-AI/tests"

result = subprocess.run(
    ["python", "-m", "pytest", test_dir, "-v", "--tb=short"],
    capture_output=True,
    text=True,
    cwd="."
)

print(f"\n📊 Pytest output:")
print(result.stdout)

# Parse pytest output for individual test results
test_results = []
lines = result.stdout.split('\n')

# Pattern: test_file.py::test_name PASSED/FAILED [duration]
pattern = r'(test_\w+\.py)::(test_\w+)\s+(PASSED|FAILED|SKIPPED)\s+.*?(\d+\.\d+)s'

for line in lines:
    match = re.search(pattern, line)
    if match:
        file_name, test_name, status, duration = match.groups()
        test_results.append({
            'test_name': f"{file_name}::{test_name}",
            'status': status,
            'duration': float(duration),
            'details': '',
            'language': 'python'
        })

# Count results
total = len(test_results)
passed = sum(1 for t in test_results if t['status'] == 'PASSED')
failed = sum(1 for t in test_results if t['status'] == 'FAILED')
skipped = sum(1 for t in test_results if t['status'] == 'SKIPPED')

print(f"\n📊 Parsed Results:")
print(f"  Total: {total}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Skipped: {skipped}")
print(f"  Test results list: {len(test_results)} items")

# Create timestamped folder
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
report_dir = Path(f"examples/sample_python_app/TestGen-AI/reports/{timestamp}")
report_dir.mkdir(parents=True, exist_ok=True)

# Create execution summary
summary = ExecutionSummary(
    project_name="sample_python_app",
    total=total,
    passed=passed,
    failed=failed,
    skipped=skipped,
    duration=0.0,
    language="python",
    results=test_results
)

# Generate report
reporter = ReportGenerator()
output_path = report_dir / "test_report.html"

reporter.generate_html(summary, str(output_path))
print(f"\n✅ Report generated: {output_path}")
print(f"📊 Open: file:///{output_path.absolute()}")
print(f"\n📁 Report saved to timestamped folder: {timestamp}")

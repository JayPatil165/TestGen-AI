#!/usr/bin/env python3
"""Generate a sample HTML report to show the new design."""
import sys
sys.path.insert(0, 'src')

from testgen.ui.reporter import ReportGenerator, ExecutionSummary
from datetime import datetime

# Create sample test results
summary = ExecutionSummary(
    project_name="Sample Python App",
    total=10,
    passed=7,
    failed=2,
    skipped=1,
    duration=5.42,
    timestamp=datetime.now(),
    language="python",
    results=[
        {'test_name': 'test_add_positive_numbers', 'status': 'PASS', 'duration': 0.12, 'details': '', 'language': 'python'},
        {'test_name': 'test_add_negative_numbers', 'status': 'PASS', 'duration':0.08, 'details': '', 'language': 'python'},
        {'test_name': 'test_subtract_basic', 'status': 'PASS', 'duration': 0.09, 'details': '', 'language': 'python'},
        {'test_name': 'test_multiply_zero', 'status': 'PASS', 'duration': 0.07, 'details': '', 'language': 'python'},
        {'test_name': 'test_divide_by_zero', 'status': 'FAIL', 'duration': 0.15, 'details': 'AssertionError: Division by zero not handled', 'language': 'python'},
        {'test_name': 'test_power_large_numbers', 'status': 'PASS', 'duration': 0.22, 'details': '', 'language': 'python'},
        {'test_name': 'test_validate_email', 'status': 'PASS', 'duration': 0.11, 'details': '', 'language': 'python'},
        {'test_name': 'test_validate_phone', 'status': 'FAIL', 'duration': 0.13, 'details': 'AssertionError: Invalid phone format not rejected', 'language': 'python'},
        {'test_name': 'test_process_data_empty', 'status': 'SKIP', 'duration': 0.00, 'details': 'Not implemented yet', 'language': 'python'},
        {'test_name': 'test_file_read_write', 'status': 'PASS', 'duration': 0.45, 'details': '', 'language': 'python'},
    ]
)

# Generate HTML report
generator = ReportGenerator()
output_path = "sample_professional_report.html"
report_path = generator.generate_html(summary, output_path)

print(f"✅ Professional report generated: {report_path}")
print("📊 Report includes:")
print("   • Blue language badge (#4A90E2)")
print("   • Subtle professional colors")
print("   • Working charts (doughnut + bar)")
print("   • 10 sample test results")
print(f"\n🌐 Open in browser: file://{report_path}")

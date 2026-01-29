#!/usr/bin/env python3
"""Generate a fresh test report with new professional colors."""
import sys
sys.path.insert(0, 'src')

from testgen.ui.reporter import ReportGenerator, ExecutionSummary
from pathlib import Path

# Create a sample execution summary with test data
summary = ExecutionSummary(
    project_name="sample_python_app",
    total=30,  # Approximate count from test files
    passed=0,
    failed=0,
    skipped=0,
    duration=0.0,
    language="python"
)

# Generate report
reporter = ReportGenerator()
output_path = Path("examples/sample_python_app/TestGen-AI/reports/test_report.html")
output_path.parent.mkdir(parents=True, exist_ok=True)

reporter.generate_html(summary, str(output_path))
print(f"✅ Report generated: {output_path}")
print(f"📊 Open in browser: file:///{output_path.absolute()}")

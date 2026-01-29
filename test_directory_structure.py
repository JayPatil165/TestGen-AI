#!/usr/bin/env python3
"""
Quick test script to verify TestGen-AI directory structure.
Tests that outputs go to: <target>/TestGen-AI/tests/ and <target>/TestGen-AI/reports/
"""
import sys
sys.path.insert(0, 'src')

from testgen.manager import WorkflowManager
from pathlib import Path

# Test with sample_python_app
project_path = "examples/sample_python_app"
config = {
    'language': 'python',
    'verbose': True,
    'use_mock_llm': True  # Force MockLLM to avoid API quota
}

print("=" * 60)
print("Testing TestGen-AI Directory Structure")
print("=" * 60)

manager = WorkflowManager(project_path=project_path, config=config)

print(f"\nProject Path: {manager.project_path}")
print(f"Output Dir (tests): {manager.output_dir}")
print(f"Report Dir: {manager.report_dir}")
print(f"Cache Dir: {manager.cache_dir}")

# Verify paths are correct
expected_base = Path(project_path) / "TestGen-AI"
assert str(manager.output_dir).endswith("TestGen-AI\\tests") or str(manager.output_dir).endswith("TestGen-AI/tests"), f"Output dir incorrect: {manager.output_dir}"
assert str(manager.report_dir).endswith("TestGen-AI\\reports") or str(manager.report_dir).endswith("TestGen-AI/reports"), f"Report dir incorrect: {manager.report_dir}"

print("\n✅ Directory structure is correct!")
print(f"   Tests will go to: {manager.output_dir}")
print(f"   Reports will go to: {manager.report_dir}")

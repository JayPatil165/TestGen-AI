#!/usr/bin/env python
"""Quick test of WorkflowManager integration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from testgen.manager import WorkflowManager

# Test configuration
workflow_config = {
    'language': 'python',
    'output_dir': 'tests',
    'verbose': True
}

print("Creating WorkflowManager...")
manager = WorkflowManager(config=workflow_config)

print("Executing generate workflow...")
try:
    result = manager.execute_generate(
        source_files=['examples/sample_python_app'],
        language='python'
    )
    print(f"\n✅ Success!")
    print(f"Result: {result}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

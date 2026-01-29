#!/usr/bin/env python3
"""Quick test of path construction."""
import sys
sys.path.insert(0, 'src')

from pathlib import Path
from testgen.manager import WorkflowManager

print("Testing path construction...")
print("=" * 60)

try:
    manager = WorkflowManager(
        project_path="examples/sample_python_app",
        config={'verbose': True}
    )
    
    print("[OK] WorkflowManager created successfully")
    print(f"   Project path: {manager.project_path}")
    print(f"   Output dir: {manager.output_dir}")
    print(f"   Report dir: {manager.report_dir}")
    print(f"   Cache dir: {manager.cache_dir}")
    print(f"\n   Output dir type: {type(manager.output_dir)}")
    print(f"   Output dir exists: {manager.output_dir.exists()}")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

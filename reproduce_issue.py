import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path("src").resolve()))

from testgen.core.python_runner import PythonTestRunner

def reproduce():
    print("Reproducing test execution issue...")
    
    # Setup runner
    runner = PythonTestRunner(verbose=True, project_dir="examples/sample_python_app")
    
    # Target specific test file/dir that we know exists from previous steps
    # We will try to find the timestamped folder dynamically or hardcode the one we just made
    test_dir = Path("examples/sample_python_app/TestGen-AI/tests")
    if not test_dir.exists():
        print(f"Test dir {test_dir} not found!")
        return

    # Find the latest timestamped folder
    subdirs = [d for d in test_dir.iterdir() if d.is_dir() and d.name != "__pycache__"]
    if not subdirs:
        print("No timestamped test directories found!")
        return
        
    latest_dir = sorted(subdirs)[-1]
    print(f"Running tests in: {latest_dir}")
    
    # Run tests
    results = runner.run_tests(str(latest_dir))
    
    print("\n--- Test Results Object ---")
    print(f"Total: {results.total}")
    print(f"Passed: {results.passed}")
    print(f"Failed: {results.failed}")
    print(f"Skipped: {results.skipped}")
    print(f"Duration: {results.duration}")
    print(f"Test Count in List: {len(results.tests)}")
    
    if len(results.tests) > 0:
        print("First test result:", results.tests[0])
    else:
        print("No tests found in results.tests list!")

if __name__ == "__main__":
    reproduce()

import subprocess
import sys
import os

def run_debug():
    print("Running pytest on examples/sample_python_app/TestGen-AI/tests/2026-02-08_22-18-54/test_calculator.py...")
    
    # Adjust path if needed
    test_file = "examples/sample_python_app/TestGen-AI/tests/2026-02-08_22-18-54/test_calculator.py"
    if not os.path.exists(test_file):
        # try find any test file
        import glob
        files = glob.glob("examples/sample_python_app/TestGen-AI/tests/**/*.py", recursive=True)
        if files:
            test_file = files[0]
            print(f"Found test file: {test_file}")
        else:
            print("No test file found!")
            return

    # Add project root to python path to match runner behavior
    env = os.environ.copy()
    project_root = os.path.abspath("examples/sample_python_app")
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
    print(f"PYTHONPATH: {env['PYTHONPATH']}")

    cmd = [sys.executable, "-m", "pytest", "-v", test_file]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        
        output = [
            "\n--- STDOUT ---",
            result.stdout,
            "\n--- STDERR ---",
            result.stderr,
            f"\nReturn Code: {result.returncode}"
        ]
        
        with open("debug_output_utf8.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
            
        print("Output written to debug_output_utf8.txt")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_debug()

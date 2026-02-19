import sys
import os

# Emulate conftest logic
root = r"D:/Programming/Projects/TestGen-AI"
if root not in sys.path:
    sys.path.insert(0, root)

print(f"Path: {sys.path}")

try:
    print("Attempting to import examples.complex_app.main...")
    from examples.complex_app.main import process_data
    print("Successfully imported process_data")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()

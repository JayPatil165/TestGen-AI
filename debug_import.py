import sys
import os

print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")

try:
    import testgen
    print(f"TestGen package found: {testgen.__file__}")
except ImportError as e:
    print(f"Failed to import testgen: {e}")

try:
    from testgen.core.scanner import CodeScanner
    print("Successfully imported CodeScanner")
    scanner = CodeScanner()
    print("Successfully instantiated CodeScanner")
except ImportError as e:
    print(f"Failed to import CodeScanner: {e}")
except Exception as e:
    print(f"Failed to instantiate CodeScanner: {e}")

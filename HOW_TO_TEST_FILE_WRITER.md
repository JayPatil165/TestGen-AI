# 🎯 How to Test the File Writer

## Quick Start

### 1. Run the Demo:
```powershell
.venv\Scripts\activate
python demo_file_writer.py
```

### 2. Find the Generated Files:
**Location:** `demo_output/tests/`

The demo creates:
- `demo_output/tests/test_calculator.py`
- `demo_output/tests/test_utils.py`
- `demo_output/tests/core/test_api.py`

### 3. View a Generated File:
```powershell
type demo_output\tests\test_calculator.py
```

Or open it in VS Code:
```powershell
code demo_output\tests\test_calculator.py
```

---

## What the File Writer Does:

✅ **Auto-creates directories** - Makes `tests/` folder automatically
✅ **Naming convention** - Converts `src/example.py` → `tests/test_example.py`
✅ **Adds headers** - Includes timestamp and source file info
✅ **Preserves structure** - `src/core/api.py` → `tests/core/test_api.py`

---

## Example Usage in Your Code:

```python
from testgen.core.file_writer import TestFileWriter

# Create writer
writer = TestFileWriter(output_dir="tests")

# Save a test file
result = writer.save_test_file(
    code=your_test_code,
    source_file="src/myfile.py"
)

print(f"Saved to: {result.file_path}")
```

---

## Directory Structure Created:

```
demo_output/
└── tests/
    ├── test_calculator.py      (634 bytes, 30 lines)
    ├── test_utils.py           (593 bytes)
    └── core/
        └── test_api.py
```

---

## Clean Up:

To remove demo files:
```powershell
Remove-Item -Recurse -Force demo_output
```

---

## Try It Yourself!

Edit `demo_file_writer.py` and add your own test:

```python
my_test = '''
def test_my_function():
    assert 1 + 1 == 2
'''

result = writer.save_test_file(
    code=my_test,
    source_file="src/myfile.py"
)
```

Then run it again!

---

**Task 41 - File Writer: FULLY WORKING!** ✅

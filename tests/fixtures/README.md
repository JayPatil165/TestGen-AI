# Test Fixtures for Code Scanner

This directory contains sample projects for testing the TestGen AI code scanner.

## Directory Structure

```
fixtures/
├── python_project/
│   ├── sample_module.py  # Classes, dataclasses, methods
│   └── utils.py          # Various function signatures
└── javascript_project/
    ├── sample.js         # Functions, classes, async/await
    └── components.jsx    # React components with hooks
```

## Python Project Fixtures

### sample_module.py
Contains:
- `@dataclass` decorator
- Class with `@property` and `@classmethod`
- Type hints (List, Optional)
- Async functions
- Multiple classes with inheritance

**Expected Extraction:**
- 2 classes: `User`, `UserService`
- 7 functions/methods
- Imports: `typing`, `dataclasses`

### utils.py
Contains:
- Simple functions
- Functions with parameters and defaults
- Functions with return type annotations
- Complex function with *args/**kwargs

**Expected Extraction:**
- 4 functions
- Various parameter combinations

## JavaScript Project Fixtures

### sample.js
Contains:
- Regular functions
- Arrow functions
- ES6 classes with extends
- Async/await
- Exports

**Expected Extraction:**
- 2 classes: `UserManager`, `AdminManager` (with extends)
- 6 functions
- Methods in classes

### components.jsx
Contains:
- React functional components
- React hooks (useState, useEffect)
- Legacy class component
- Component props

**Expected Extraction:**
- 3 components: `UserProfile`, `Dashboard`, `LegacyComponent`
- Hooks detected: State, Effect
- Methods in class component

## Usage in Tests

```python
from testgen.core.scanner import CodeScanner

# Scan Python project
scanner = CodeScanner()
result = scanner.scan_directory('./tests/fixtures/python_project')

assert result.total_files == 2
assert len(result.files) == 2

# Check Python extraction
python_file = [f for f in result.files if f.file_type.value == '.py'][0]
assert len(python_file.functions) > 0
assert len(python_file.classes) > 0

# Scan JavaScript project
result = scanner.scan_directory('./tests/fixtures/javascript_project')

assert result.total_files == 2
js_file = [f for f in result.files if f.file_type.value == '.js'][0]
assert len(js_file.functions) > 0
```

## Coverage

These fixtures test:
- ✅ Multi-language support (Python, JavaScript, React)
- ✅ Function signature extraction
- ✅ Class structure extraction
- ✅ Decorator detection (@dataclass, @property)
- ✅ Type hint extraction
- ✅ Hook detection (React)
- ✅ Inheritance (extends)
- ✅ Async function detection
- ✅ Import statement extraction

## Adding New Fixtures

When adding new test fixtures:
1. Create the file in the appropriate project directory
2. Include diverse code constructs  
3. Add comments explaining what should be extracted
4. Update this README with expected results
5. Add corresponding tests in `test_scanner.py`

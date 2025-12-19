# 🌍 Multi-Language Test Runner - Architecture Guide

## Overview

TestGen AI now supports **multi-language test generation and execution**! The system automatically detects your project's programming language and uses the appropriate test runner.

---

## 🎯 Supported Languages

### ✅ **Currently Supported:**
- **Python** (pytest)
- **JavaScript** (Jest)
- **TypeScript** (Jest)

### 🔜 **Coming Soon:**
- Java (JUnit, TestNG)
- Go (go test)
- C# (NUnit, xUnit, MSTest)
- Ruby (RSpec, Minitest)

---

## 🏗️ Architecture

### **1. Language Detection**
`src/testgen/core/language_detector.py`

Automatically detects programming language from:
- Project files (package.json, requirements.txt, pom.xml, etc.)
- File extensions
- Configuration files

```python
from testgen.core.language_detector import LanguageDetector

detector = LanguageDetector()
language = detector.detect_language("./my-project")
framework = detector.detect_test_framework("./my-project")
```

### **2. Base Runner Interface**
`src/testgen/core/base_runner.py`

Abstract base class defining the common interface:
```python
class BaseTestRunner(ABC):
    @abstractmethod
    def run_tests(test_dir, pattern) -> TestResults
    
    @abstractmethod
    def discover_tests(test_dir, pattern) -> List[Path]
    
    @abstractmethod
    def count_tests(test_dir, pattern) -> int
    
    @abstractmethod
    def build_command(test_dir, pattern) -> List[str]
```

### **3. Language-Specific Runners**

#### **Python Runner**
`src/testgen/core/python_runner.py`
- Uses pytest
- Supports pytest-cov for coverage
- Supports pytest-xdist for parallel execution
- Patterns: `test_*.py`, `*_test.py`

#### **JavaScript/TypeScript Runner**
`src/testgen/core/javascript_runner.py`
- Uses Jest
- Auto-detects TypeScript
- Built-in coverage support
- Patterns: `*.test.js`, `*.spec.js`, `**/__tests__/**/*.js`

### **4. Runner Factory**
`src/testgen/core/runner_factory.py`

Automatically creates the right runner:
```python
from testgen.core.runner_factory import create_test_runner

# Auto-detects language and creates appropriate runner
runner = create_test_runner("./my-project")
results = runner.run_tests("tests/")
```

---

## 📊 Common Interface (Language-Agnostic)

All runners return the same `TestResults` format:

```python
@dataclass
class TestResults:
    tests: List[TestResult]
    total: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    language: str  # "python", "javascript", etc.
    framework: str  # "pytest", "jest", etc.
```

---

## 🚀 Usage Examples

### **Automatic Detection**
```python
from testgen.core.runner_factory import create_test_runner

# The factory detects your language automatically
runner = create_test_runner("./my-project")
results = runner.run_tests("tests/")

print(f"Language: {results.language}")
print(f"Framework: {results.framework}")
print(f"Passed: {results.passed}/{results.total}")
```

### **Python Project**
```python
from testgen.core.python_runner import PythonTestRunner

runner = PythonTestRunner(verbose=True)
results = runner.run_tests("tests/", pattern="test_*.py")
```

### **JavaScript Project**
```python
from testgen.core.javascript_runner import JavaScriptTestRunner

runner = JavaScriptTestRunner(verbose=True)
results = runner.run_tests("tests/", pattern="*.test.js")
```

---

## 🎨 Benefits

### **For Users:**
- ✅ **Zero Configuration**: Auto-detects your language
- ✅ **Consistent Interface**: Same API across all languages
- ✅ **Future-Proof**: Easy to add new languages

### **For Developers:**
- ✅ **Clean Architecture**: Abstract base class + specific implementations
- ✅ **Easy Extension**: Just implement `BaseTestRunner`
- ✅ **Testable**: Each runner is independently testable

---

## 📝 Adding a New Language

To add support for a new language:

1. **Update Language Detector** (`language_detector.py`):
   ```python
   # Add to Language enum
   KOTLIN = "kotlin"
   
   # Add detection logic
   LANGUAGE_FILES = {
       "build.gradle.kts": Language.KOTLIN,
   }
   ```

2. **Create Language Runner** (`kotlin_runner.py`):
   ```python
   class KotlinTestRunner(BaseTestRunner):
       def run_tests(self, test_dir, pattern) -> TestResults:
           # Implementation
           pass
       
       # Implement other abstract methods...
   ```

3. **Update Factory** (`runner_factory.py`):
   ```python
   if language == Language.KOTLIN:
       return KotlinTestRunner(verbose=verbose)
   ```

---

## 🔧 Technical Details

### **Language Detection Priority:**
1. Check for language-specific files (package.json, requirements.txt, etc.)
2. Check file extensions (`.py`, `.js`, `.java`, etc.)
3. Fallback to Python (default)

### **TestFramework Detection:**
- Checks dependencies (`package.json`, `requirements.txt`, etc.)
- Looks for config files (`jest.config.js`, `pytest.ini`, etc.)
- Analyzes test file imports

### **Command Building:**
- Each runner builds language-specific commands
- Python: `python -m pytest`
- JavaScript: `npm test` or `jest`
- All output captured for parsing

---

## 📈 Future Enhancements

- [ ] Java support (JUnit, TestNG)
- [ ] Go support (go test)
- [ ] C# support (NUnit, xUnit, MSTest)
- [ ] Ruby support (RSpec, Minitest)
- [ ] Rust support (cargo test)
- [ ] PHP support (PHPUnit)

---

## 🎯 Design Principles

1. **Language-Agnostic Interface**: Common API for all languages
2. **Auto-Detection**: No manual configuration needed
3. **Extensible**: Easy to add new languages
4. **Consistent Results**: Same TestResults format everywhere
5. **Framework Flexibility**: Support multiple frameworks per language

---

This architecture makes TestGen AI truly **multi-language** and ready for any project! 🚀

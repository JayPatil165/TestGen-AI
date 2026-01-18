# Manual Testing Protocol for Watch Mode
## Universal Multi-Language Support (ALL 14 Languages)

This document provides a comprehensive manual testing protocol for the TestGen AI watch mode across all 14 supported programming languages.

---

## Overview

**Watch Mode Components to Test:**
- File Watcher (detects file changes)
- Change Detector (filters and classifies changes)
- Smart Invalidator (decides when to regenerate)
- Incremental Processor (processes single files)
- Feedback System (real-time status updates)
- Auto Runner (runs generated tests)
- Rate Limiter (manages API calls)
- Shutdown Handler (graceful exit)

**Languages Covered:** Python, JavaScript, TypeScript, Java, Go, C#, Ruby, Rust, PHP, Swift, Kotlin, C++, HTML, CSS

---

## Prerequisites

### Required Installations

```bash
# Core
pip install watchdog pydantic

# Language-specific test runners (install as needed)
pip install pytest                  # Python
npm install -g jest                 # JavaScript/TypeScript
# Maven/Gradle for Java
# go test (built-in)
# dotnet test (built-in C#)
gem install rspec                   # Ruby
# cargo test (built-in Rust)
composer require phpunit/phpunit    # PHP
# swift test (built-in)
# gradle for Kotlin
# googletest for C++
```

### Project Setup

1. Navigate to a real project directory
2. Ensure test framework is installed for your language
3. Have LLM API keys configured (if testing generation)

---

## Test Protocol

### Phase 1: Basic File Detection (All Languages)

**Objective:** Verify watch mode detects file changes across all languages

#### Test 1.1: Python File Detection

```bash
# Start watch mode (when implemented)
testgen watch --language python

# In another terminal:
# 1. Create a new Python file
echo "def calculate(x): return x * 2" > src/utils.py

# Expected Output:
# 📝 Detected change in source file: utils.py
# 🌍 PYTHON - ⚙️ Generating tests for utils.py...
# ✓ Tests updated: test_utils.py (2.3s)
```

**Verify:**
- [ ] File change detected
- [ ] Language correctly identified as Python
- [ ] Classified as source file (not test)
- [ ] Test generation triggered
- [ ] Test file created at correct path

#### Test 1.2: JavaScript File Detection

```bash
# Start watch mode
testgen watch --language javascript

# Create JavaScript file
echo "function add(a, b) { return a + b; }" > src/calculator.js

# Expected Output:
# 📝 Detected change in source file: calculator.js
# 🌍 JAVASCRIPT - ⚙️ Generating tests for calculator.js...
# ✓ Tests updated: calculator.test.js (1.8s)
```

**Verify:**
- [ ] JavaScript file detected
- [ ] Correct naming: `*.test.js`
- [ ] Jest-compatible test format

#### Test 1.3: Java File Detection

```bash
# Create Java class
cat > src/Calculator.java << EOF
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
EOF

# Expected Output:
# 📝 Detected change in source file: Calculator.java
# 🌍 JAVA - ⚙️ Generating tests for Calculator.java...
# ✓ Tests updated: CalculatorTest.java (2.1s)
```

**Verify:**
- [ ] Java file detected
- [ ] Correct naming: `*Test.java`
- [ ] JUnit-compatible test format

#### Test 1.4: Go File Detection

```bash
# Create Go file
cat > calculator.go << EOF
package main

func Add(a, b int) int {
    return a + b
}
EOF

# Expected Output:
# 📝 Detected change in source file: calculator.go
# 🌍 GO - ⚙️ Generating tests for calculator.go...
# ✓ Tests updated: calculator_test.go (1.5s)
```

**Verify:**
- [ ] Go file detected
- [ ] Correct naming: `*_test.go`
- [ ] Go testing package format

#### Test 1.5-1.14: Remaining Languages

**Repeat for:**
- TypeScript (*.test.ts)
- C# (*Tests.cs)
- Ruby (*_spec.rb)
- Rust (*_test.rs)
- PHP (*Test.php)
- Swift (*Tests.swift)
- Kotlin (*Test.kt)
- C++ (*_test.cpp)
- HTML (test_*.html)
- CSS (test_*.css)

---

### Phase 2: Debouncing Logic

**Objective:** Verify rapid changes are debounced

#### Test 2.1: Rapid File Modifications

```bash
# Start watch mode with visible debouncing
testgen watch --debounce 2.0

# Rapidly modify file 5 times
for i in {1..5}; do
    echo "# Modification $i" >> src/test.py
    sleep 0.2
done

# Expected Output:
# 📝 Detected change in source file: test.py
# (only ONE detection, not 5, due to 2s debounce)
```

**Verify:**
- [ ] Only 1-2 detections (not 5)
- [ ] Debounce timer working
- [ ] Batch processing activated

---

### Phase 3: Smart Invalidation

**Objective:** Verify test files don't trigger regeneration

#### Test 3.1: Modify Test File

```bash
# Modify a test file
echo "# New test comment" >> tests/test_calculator.py

# Expected Output:
# ⏩ Skipping test_calculator.py: Test file (not source)
```

**Verify:**
- [ ] Change detected
- [ ] Classified as test file
- [ ] Skip decision made
- [ ] No test generation triggered

#### Test 3.2: Modify Source File

```bash
# Modify source file
echo "# New function" >> src/calculator.py

# Expected Output:
# 📝 Detected change in source file: calculator.py
# 🌍 PYTHON - ⚙️ Generating tests for calculator.py...
# ✓ Tests updated: test_calculator.py
```

**Verify:**
- [ ] Classified as source file
- [ ] Regenerate decision made
- [ ] Test generation triggered

#### Test 3.3: Delete Source File

```bash
# Delete source file
rm src/calculator.py

# Expected Output:
# 🗑️ Source file deleted: calculator.py
# Suggestion: Delete corresponding test file test_calculator.py
```

**Verify:**
- [ ] Deletion detected
- [ ] DELETE_TEST action suggested
- [ ] No generation triggered

---

### Phase 4: Rate Limiting

**Objective:** Verify API call rate limiting works

#### Test 4.1: Queue Multiple Changes

```bash
# Start watch with low rate limit
testgen watch --max-requests 3

# Create 10 files rapidly
for i in {1..10}; do
    echo "def func_$i(): pass" > src/file_$i.py
    sleep 0.1
done

# Expected Output:
# ⏳ Queued: file_1.py (queue: 1)
# ⏳ Queued: file_2.py (queue: 2)
# ...
# 📦 Batching: file_1.py (1/5)
# 📦 Batching: file_2.py (2/5)
# 🔄 Processing batch of 5 changes...
# ⏸️ Rate limit reached, waiting...
```

**Verify:**
- [ ] Files queued
- [ ] Batching activated
- [ ] Rate limit enforced
- [ ] Queue processed after delay

---

### Phase 5: Feedback System

**Objective:** Verify real-time status updates

#### Test 5.1: Status Messages

```bash
# Monitor all feedback messages
testgen watch --verbose

# Make changes and verify output format
```

**Expected Messages:**
- `📝 Detected change in <file>`
- `⚙️ Generating tests for <file>...`
- `✓ Tests updated: <test_file> (X.Xs)`
- `⏩ Skipping <file>: <reason>`
- `❌ Error: <error_message>`

**Verify:**
- [ ] All message types appear
- [ ] Language names shown
- [ ] Timing information included
- [ ] Icons display correctly

#### Test 5.2: Statistics

```bash
# Run for a while then check stats
# (Press Ctrl+C to trigger shutdown)

# Expected Output:
# 📊 Session Statistics:
#    Changes detected: 15
#    Tests generated: 12
#    Errors: 0
#    Languages: python, javascript
```

**Verify:**
- [ ] Accurate counts
- [ ] Language breakdown
- [ ] Error tracking

---

### Phase 6: Auto-Run Tests

**Objective:** Verify generated tests run automatically

#### Test 6.1: Auto-Run Configuration

```bash
# Start with auto-run enabled
testgen watch --auto-run

# Create file
echo "def add(a, b): return a + b" > src/math.py

# Expected Output:
# 📝 Detected change in source file: math.py
# ⚙️ Generating tests for math.py...
# ✓ Tests updated: test_math.py (2.1s)
# 🏃 Running tests: test_math.py...
# ✅ Tests passed: test_math.py (3 passed, 0.5s)
```

**Verify:**
- [ ] Tests generated
- [ ] Tests executed automatically
- [ ] Results displayed
- [ ] Pass/fail count shown

---

### Phase 7: Shutdown Behavior

**Objective:** Verify graceful shutdown

#### Test 7.1: Normal Shutdown (Ctrl+C)

```bash
# Start watch mode
testgen watch

# Press Ctrl+C

# Expected Output:
# 🛑 Shutdown initiated (Ctrl+C detected)...
#    Stopping 1 watcher(s)...
#    Stopping 1 detector(s)...
#    State saved to .testgen_state.json
# 📊 Session Statistics:
#    Changes detected: 5
#    Tests generated: 4
# ✅ Shutdown complete. Goodbye!
```

**Verify:**
- [ ] Watchers stopped
- [ ] Detectors stopped
- [ ] State saved
- [ ] Statistics shown
- [ ] Clean exit

#### Test 7.2: Force Quit (Double Ctrl+C)

```bash
# Start watch mode
testgen watch

# Press Ctrl+C twice rapidly

# Expected Output:
# 🛑 Shutdown initiated...
# ⚠️ Force quitting...
# (immediate exit)
```

**Verify:**
- [ ] First Ctrl+C starts shutdown
- [ ] Second Ctrl+C forces immediate exit

---

### Phase 8: Performance Testing

**Objective:** Test with many files

#### Test 8.1: Large Project

```bash
# Navigate to large project (100+ files)
cd /path/to/large/project

# Start watch mode
testgen watch

# Modify several files
# Monitor memory and CPU usage
```

**Verify:**
- [ ] No memory leaks
- [ ] Reasonable CPU usage (<10%)
- [ ] Responsive to changes
- [ ] No crashes

#### Test 8.2: Concurrent Changes

```bash
# Use a script to modify multiple files simultaneously
# Verify watch mode handles concurrent events
```

**Verify:**
- [ ] All changes detected
- [ ] No race conditions
- [ ] Queue handles concurrency
- [ ] Thread-safe operations

---

### Phase 9: Multi-Language Project

**Objective:** Test polyglot project

#### Test 9.1: Mixed Language Project

```bash
# In project with multiple languages
# Directory structure:
# - backend/ (Python)
# - frontend/ (JavaScript)
# - services/ (Go)
# - tests/

testgen watch --languages python,javascript,go

# Modify files in different languages
# Verify each is handled correctly
```

**Verify:**
- [ ] All languages detected
- [ ] Correct language identification
- [ ] Language-specific test generation
- [ ] Proper file path mapping

---

### Phase 10: Edge Cases

#### Test 10.1: Binary Files

```bash
# Copy binary file
cp image.png src/

# Expected: Ignored (not code)
```

**Verify:**
- [ ] Binary files ignored
- [ ] No generation triggered

#### Test 10.2: Very Large Files

```bash
# Create large file (>1MB)
# Verify handling
```

**Verify:**
- [ ] Large files handled
- [ ] No timeout issues

#### Test 10.3: Special Characters in Filenames

```bash
# Create file with spaces
echo "code" > "my file.py"
```

**Verify:**
- [ ] Special characters handled
- [ ] No path errors

---

## Test Checklist Summary

### By Language

- [ ] Python - File detection, test generation, auto-run
- [ ] JavaScript - File detection, test generation, auto-run
- [ ] TypeScript - File detection, test generation, auto-run
- [ ] Java - File detection, test generation, auto-run
- [ ] Go - File detection, test generation, auto-run
- [ ] C# - File detection, test generation, auto-run
- [ ] Ruby - File detection, test generation, auto-run
- [ ] Rust - File detection, test generation, auto-run
- [ ] PHP - File detection, test generation, auto-run
- [ ] Swift - File detection, test generation, auto-run
- [ ] Kotlin - File detection, test generation, auto-run
- [ ] C++ - File detection, test generation, auto-run
- [ ] HTML - File detection, test generation
- [ ] CSS - File detection, test generation

### By Feature

- [ ] File watching (all languages)
- [ ] Change detection (filtering, classification)
- [ ] Debouncing (rapid changes)
- [ ] Smart invalidation (test vs source)
- [ ] Rate limiting (queue, batch)
- [ ] Feedback (messages, statistics)
- [ ] Auto-run (test execution)
- [ ] Shutdown (graceful, force)
- [ ] Performance (large projects)
- [ ] Multi-language (polyglot projects)

---

## Success Criteria

✅ **All languages detected correctly**  
✅ **Test files generated with correct naming**  
✅ **Debouncing prevents rapid triggers**  
✅ **Test files don't trigger regeneration**  
✅ **Rate limiting prevents API overload**  
✅ **Real-time feedback displays correctly**  
✅ **Auto-run executes and reports results**  
✅ **Graceful shutdown saves state**  
✅ **Performance acceptable in large projects**  
✅ **Multi-language projects handled correctly**

---

## Troubleshooting

### Issue: Changes not detected
- Check watchdog is installed: `pip install watchdog`
- Verify directory permissions
- Check ignore patterns

### Issue: Wrong language detected
- Verify file extension
- Check Language enum mappings
- Review language_config.py

### Issue: Tests not generated
- Check LLM API keys
- Verify rate limiting not blocking
- Check error messages

### Issue: Too many API calls
- Adjust rate limit: `--max-requests 5`
- Increase batch delay: `--batch-delay 3.0`
- Review queuing logic

---

## Notes

- Manual testing should be performed before each release
- Test on multiple operating systems (Windows, macOS, Linux)
- Verify with actual projects, not just test files
- Document any issues or unexpected behavior
- Update protocol as features change

**Version:** 1.0  
**Last Updated:** 2026-01-14  
**Languages Supported:** 14

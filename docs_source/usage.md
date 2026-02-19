# Usage Guide

TestGen AI provides a set of powerful commands to manage your testing lifecycle.

## Basic Commands

### 🎯 Auto Workflow (Recommended)
Run the full autonomous loop: Scan → Generate → Test → Report.
```bash
testgen auto ./src
```

### 🔍 Generate Tests
Analyze source code and generate tests without running them.
```bash
testgen generate ./src
```

### 🧪 Run Tests
Discover and execute generated tests.
```bash
testgen test ./tests
```

### 📊 Generate Report
Create a beautiful HTML report from the latest test results.
```bash
testgen report ./tests
```

## Advanced Options

### Watch Mode
Monitor files in real-time and regenerate tests on save.
```bash
testgen generate ./src --watch
```

### Verbose Output
See exactly what TestGen AI is doing under the hood.
```bash
testgen --verbose generate ./src
```

### Dry Run
See which files would be affected without making any changes.
```bash
testgen generate ./src --dry-run
```

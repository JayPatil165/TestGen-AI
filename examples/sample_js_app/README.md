# Sample JavaScript Application

This is a sample JavaScript/Node.js application for testing the TestGen AI test generation tool.

## Modules

1. **mathUtils.js** - Mathematical operations (beginner level)
2. **arrayHelpers.js** - Array manipulation utilities (intermediate level)
3. **stringFormatter.js** - String formatting functions (intermediate level)
4. **objectUtils.js** - Object manipulation utilities (intermediate-advanced level)

## Usage

This project demonstrates JavaScript/Node.js modules to test the AI's test generation capabilities for JavaScript.

### Run TestGen on this project:

```bash
# Generate tests for all modules
testgen generate examples/sample_js_app/ --language javascript

# Generate and run tests automatically
testgen auto examples/sample_js_app/ --language javascript

# Generate with specific output directory
testgen generate examples/sample_js_app/ --language javascript --output tests/
```

## Complexity Levels

- **Simple**: mathUtils.js - Basic functions with minimal logic
- **Medium**: arrayHelpers.js, stringFormatter.js - More complex logic, array operations
- **Complex**: objectUtils.js - Object manipulation, deep operations

## Total Functions

- 20 functions across 4 modules
- CommonJS module format
- Ready for test generation and execution

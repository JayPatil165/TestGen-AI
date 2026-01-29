# Sample Python Application

This is a sample Python application for testing the TestGen AI test generation tool.

## Modules

1. **calculator.py** - Simple arithmetic operations (beginner level)
2. **string_utils.py** - String manipulation utilities (intermediate level)
3. **data_processor.py** - Data processing and analysis (intermediate-advanced level)
4. **file_handler.py** - File operations and JSON handling (advanced level)
5. **validator.py** - Input validation functions (intermediate level)

## Usage

This project demonstrates various complexity levels to test the AI's test generation capabilities across different scenarios.

### Run TestGen on this project:

```bash
# Generate tests for all modules
testgen generate examples/sample_python_app/

# Generate and run tests automatically
testgen auto examples/sample_python_app/

# Generate with specific language
testgen generate examples/sample_python_app/ --language python
```

## Complexity Levels

- **Simple**: calculator.py - Basic functions with minimal logic
- **Medium**: string_utils.py, validator.py - More complex logic, edge cases
- **Complex**: data_processor.py, file_handler.py - Type hints, error handling, file I/O

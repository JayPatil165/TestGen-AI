# Prompt Templates

This directory contains prompt templates for LLM-based test generation.

## Files

### 1. `system_instruction.txt`
**Purpose**: Defines the system-level behavior for the LLM.
- Sets the role (QA engineer)
- Defines quality standards
- Establishes output format

**Usage**: Sent as the system message to the LLM.

### 2. `test_generation.txt`
**Purpose**: Main prompt template for generating tests.
- Detailed guidelines for test coverage
- Test structure requirements
- Code quality standards
- Output format specifications

**Variables**:
- `{code_context}`: The code to generate tests for

**Usage**: 
```python
prompt = template.format(code_context=scanned_code)
```

### 3. `few_shot_examples.txt`
**Purpose**: Provides examples of high-quality test generation.
- Shows expected patterns
- Demonstrates best practices
- Includes 3 detailed examples

**Usage**: Can be included in prompts for better results (optional).

## Template Variables

All templates support the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{code_context}` | Code to test | Function/class code |
| `{file_path}` | File being tested | `src/utils.py` |
| `{framework}` | Test framework | `pytest` |
| `{coverage_target}` | Coverage goal | `80` |

## Usage Examples

### Basic Generation:
```python
from testgen.prompts import load_template

# Load template
template = load_template("test_generation.txt")

# Fill in variables
prompt = template.format(
    code_context=code_to_test
)

# Generate
response = llm.generate(
    system_prompt=load_template("system_instruction.txt"),
    prompt=prompt
)
```

### With Few-Shot Examples:
```python
# Include examples for better quality
examples = load_template("few_shot_examples.txt")
prompt = f"{examples}\n\n{template.format(code_context=code)}"
```

## Best Practices

1. **System Instruction**: Always use for consistent behavior
2. **Code Context**: Include relevant imports and dependencies
3. **Few-Shot**: Use for complex code or when quality isn't meeting standards
4. **Temperature**: Use 0.2-0.4 for consistent, reliable test generation
5. **Max Tokens**: Allocate 1500-2500 tokens for comprehensive tests

## Customization

Templates can be customized for specific needs:

- **Language-specific**: Create templates for different languages
- **Framework-specific**: Adapt for unittest, jest, etc.
- **Project-specific**: Add project conventions and patterns

## Template Design Principles

1. **Clear Instructions**: Be explicit about what to generate
2. **Output Format**: Specify exact format requirements
3. **Examples**: Show, don't just tell
4. **Constraints**: Define what NOT to include
5. **Best Practices**: Educate the LLM on quality standards

## Maintenance

- Review generated tests regularly
- Update templates based on common issues
- Add new examples as patterns emerge
- Version control all changes

---

**Note**: These templates are optimized for Gemini 2.5 Flash but work with all supported LLMs.

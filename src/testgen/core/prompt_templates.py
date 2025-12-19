"""
Multi-Language Prompt Templates for Test Generation.

Provides language-specific prompts for generating tests in different languages.
"""

from typing import Dict, Any
from .language_config import Language, get_language_config


class PromptTemplates:
    """
    Multi-language prompt templates.
    
    Generates appropriate prompts for each language and test framework.
    """
    
    # Python (pytest) template
    PYTHON_PYTEST = """You are an expert Python developer writing comprehensive pytest tests.

Generate pytest unit tests for the following Python code:

```python
{code}
```

Requirements:
- Use pytest framework
- Include imports (pytest, unittest.mock if needed)
- Write descriptive test function names (test_<functionality>)
- Add docstrings to test functions
- Cover edge cases and error conditions
- Use assert statements
- Mock external dependencies if needed

Generate ONLY the test code, no explanations."""

    # JavaScript (Jest) template
    JAVASCRIPT_JEST = """You are an expert JavaScript developer writing comprehensive Jest tests.

Generate Jest unit tests for the following JavaScript code:

```javascript
{code}
```

Requirements:
- Use Jest framework
- Include necessary imports
- Use describe() and test() or it() blocks
- Write descriptive test names
- Cover edge cases and error conditions
- Use expect() assertions
- Mock dependencies with jest.fn() or jest.mock() if needed

Generate ONLY the test code, no explanations."""

    # TypeScript (Jest) template
    TYPESCRIPT_JEST = """You are an expert TypeScript developer writing comprehensive Jest tests.

Generate Jest unit tests for the following TypeScript code:

```typescript
{code}
```

Requirements:
- Use Jest framework with TypeScript
- Include proper type annotations
- Include necessary imports
- Use describe() and test() or it() blocks
- Write descriptive test names
- Cover edge cases and error conditions
- Use expect() assertions with TypeScript types
- Mock dependencies appropriately

Generate ONLY the test code, no explanations."""

    # Java (JUnit) template
    JAVA_JUNIT = """You are an expert Java developer writing comprehensive JUnit tests.

Generate JUnit 5 unit tests for the following Java code:

```java
{code}
```

Requirements:
- Use JUnit 5 framework
- Include necessary imports (org.junit.jupiter.api.*)
- Use @Test annotations
- Write descriptive test method names (should follow naming convention)
- Cover edge cases and error conditions
- Use assertions (assertEquals, assertTrue, etc.)
- Use @BeforeEach and @AfterEach if needed
- Mock dependencies with Mockito if needed

Generate ONLY the test code, no explanations."""

    # Go template
    GO_TESTING = """You are an expert Go developer writing comprehensive tests.

Generate Go unit tests for the following Go code:

```go
{code}
```

Requirements:
- Use Go's built-in testing package
- Test file should be named *_test.go
- Test functions should start with Test
- Use t.Run() for subtests
- Cover edge cases and error conditions
- Use proper error checking
- Use table-driven tests where appropriate

Generate ONLY the test code, no explanations."""

    # C# (NUnit) template
    CSHARP_NUNIT = """You are an expert C# developer writing comprehensive NUnit tests.

Generate NUnit unit tests for the following C# code:

```csharp
{code}
```

Requirements:
- Use NUnit framework
- Include necessary using statements
- Use [Test] attributes
- Write descriptive test method names
- Cover edge cases and error conditions
- Use Assert methods (Assert.AreEqual, Assert.IsTrue, etc.)
- Use [SetUp] and [TearDown] if needed
- Mock dependencies with Moq if needed

Generate ONLY the test code, no explanations."""

    # Ruby (RSpec) template
    RUBY_RSPEC = """You are an expert Ruby developer writing comprehensive RSpec tests.

Generate RSpec unit tests for the following Ruby code:

```ruby
{code}
```

Requirements:
- Use RSpec framework
- Use describe and context blocks
- Use it blocks for individual tests
- Write descriptive test names
- Cover edge cases and error conditions
- Use expect() syntax
- Use let() for test data
- Mock dependencies if needed

Generate ONLY the test code, no explanations."""

    # Rust template
    RUST_CARGO = """You are an expert Rust developer writing comprehensive tests.

Generate Rust unit tests for the following Rust code:

```rust
{code}
```

Requirements:
- Use Rust's built-in test framework
- Use #[test] attribute
- Test functions should be in a tests module
- Write descriptive test names
- Cover edge cases and error conditions
- Use assert!, assert_eq!, assert_ne!
- Use #[should_panic] for panic tests

Generate ONLY the test code, no explanations."""

    # PHP (PHPUnit) template
    PHP_PHPUNIT = """You are an expert PHP developer writing comprehensive PHPUnit tests.

Generate PHPUnit unit tests for the following PHP code:

```php
{code}
```

Requirements:
- Use PHPUnit framework
- Extend TestCase class
- Use proper namespaces
- Test methods should start with test
- Cover edge cases and error conditions
- Use assertion methods (assertEquals, assertTrue, etc.)
- Use setUp() and tearDown() if needed

Generate ONLY the test code, no explanations."""

    # Swift (XCTest) template
    SWIFT_XCTEST = """You are an expert Swift developer writing comprehensive XCTest tests.

Generate XCTest unit tests for the following Swift code:

```swift
{code}
```

Requirements:
- Use XCTest framework
- Import XCTest
- Extend XCTestCase class
- Test methods should start with test
- Cover edge cases and error conditions
- Use XCTAssert methods (XCTAssertEqual, XCTAssertTrue, etc.)
- Use setUp() and tearDown() if needed

Generate ONLY the test code, no explanations."""

    # Kotlin (JUnit) template
    KOTLIN_JUNIT = """You are an expert Kotlin developer writing comprehensive JUnit tests.

Generate JUnit unit tests for the following Kotlin code:

```kotlin
{code}
```

Requirements:
- Use JUnit framework
- Include necessary imports
- Use @Test annotations
- Write descriptive test method names
- Cover edge cases and error conditions
- Use assertions (assertEquals, assertTrue, etc.)
- Leverage Kotlin features

Generate ONLY the test code, no explanations."""

    # C++ (Google Test) template
    CPP_GTEST = """You are an expert C++ developer writing comprehensive Google Test tests.

Generate Google Test unit tests for the following C++ code:

```cpp
{code}
```

Requirements:
- Use Google Test framework
- Include gtest/gtest.h
- Use TEST() macros
- Write descriptive test names
- Cover edge cases and error conditions
- Use ASSERT and EXPECT macros

Generate ONLY the test code, no explanations."""

    # HTML (Playwright) template
    HTML_PLAYWRIGHT = """You are an expert web developer writing comprehensive Playwright tests.

Generate Playwright tests for the following HTML code:

```html
{code}
```

Requirements:
- Use Playwright framework
- Test DOM structure
- Test interactions
- Use descriptive test names
- Cover edge cases

Generate ONLY the test code, no explanations."""

    # CSS template
    CSS_VISUAL = """You are an expert CSS developer writing comprehensive visual tests.

Generate visual tests for the following CSS code:

```css
{code}
```

Requirements:
- Test visual appearance
- Test responsive design
- Use descriptive test names
- Document expected behavior

Generate ONLY the test code, no explanations."""

    # Template mapping
    TEMPLATES = {
        (Language.PYTHON, "pytest"): PYTHON_PYTEST,
        (Language.JAVASCRIPT, "jest"): JAVASCRIPT_JEST,
        (Language.TYPESCRIPT, "jest"): TYPESCRIPT_JEST,
        (Language.JAVA, "junit"): JAVA_JUNIT,
        (Language.GO, "testing"): GO_TESTING,
        (Language.CSHARP, "nunit"): CSHARP_NUNIT,
        (Language.RUBY, "rspec"): RUBY_RSPEC,
        (Language.RUST, "cargo"): RUST_CARGO,
        (Language.PHP, "phpunit"): PHP_PHPUNIT,
        (Language.SWIFT, "xctest"): SWIFT_XCTEST,
        (Language.KOTLIN, "junit"): KOTLIN_JUNIT,
        (Language.CPP, "gtest"): CPP_GTEST,
        (Language.HTML, "playwright"): HTML_PLAYWRIGHT,
        (Language.CSS, "stylelint"): CSS_VISUAL,
    }
    
    @classmethod
    def get_prompt(
        cls,
        language: Language,
        code: str,
        framework: str = None
    ) -> str:
        """
        Get prompt template for language and framework.
        
        Args:
            language: Programming language
            code: Code to generate tests for
            framework: Test framework (optional, uses default)
            
        Returns:
            Formatted prompt string
        """
        # Get language config
        config = get_language_config(language)
        
        # Use default framework if not specified
        if framework is None:
            framework = config.default_framework
        
        # Get template
        template = cls.TEMPLATES.get(
            (language, framework),
            cls.PYTHON_PYTEST  # Fallback
        )
        
        # Format with code
        return template.format(code=code)
    
    @classmethod
    def get_prompt_for_function(
        cls,
        language: Language,
        function_code: str,
        function_name: str,
        framework: str = None
    ) -> str:
        """
        Get prompt for testing a specific function.
        
        Args:
            language: Programming language
            function_code: Function code
            function_name: Function name
            framework: Test framework
            
        Returns:
            Formatted prompt
        """
        base_prompt = cls.get_prompt(language, function_code, framework)
        
        # Add function-specific context
        additional_context = f"\n\nFocus on thoroughly testing the `{function_name}` function."
        
        return base_prompt + additional_context
    
    @classmethod
    def get_prompt_for_class(
        cls,
        language: Language,
        class_code: str,
        class_name: str,
        framework: str = None
    ) -> str:
        """
        Get prompt for testing a class.
        
        Args:
            language: Programming language
            class_code: Class code
            class_name: Class name
            framework: Test framework
            
        Returns:
            Formatted prompt
        """
        base_prompt = cls.get_prompt(language, class_code, framework)
        
        # Add class-specific context
        additional_context = f"\n\nFocus on testing all methods of the `{class_name}` class."
        
        return base_prompt + additional_context

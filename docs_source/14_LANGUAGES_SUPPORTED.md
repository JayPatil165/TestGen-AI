# Comprehensive Language Support

TestGen-AI provides native integration for 14 programming and markup languages. Each language is supported through a specialized adapter that handles file detection, context extraction, and test execution orchestration.

## Supported Languages and Frameworks

| Language | Test Framework | Support Level |
|----------|----------------|---------------|
| Python | pytest | Full Support |
| JavaScript | Jest | Full Support |
| TypeScript | Jest | Full Support |
| Java | JUnit 5 | Integrated |
| Go | go test | Integrated |
| Rust | cargo test | Integrated |
| C# | NUnit / xUnit | Integrated |
| Ruby | RSpec | Integrated |
| PHP | PHPUnit | Integrated |
| Swift | XCTest | Integrated |
| Kotlin | JUnit | Integrated |
| C++ | Google Test | Integrated |
| HTML | Playwright | Experimental |
| CSS | Stylelint | Experimental |

## Language-Specific Configurations

TestGen-AI automatically detects the project language based on file extensions and project metadata (e.g., `pyproject.toml`, `package.json`, `Cargo.toml`). Users can override detection by specifying the language via the global configuration file or command-line arguments.

## Support Definitions

- **Full Support**: Advanced context extraction (classes, methods, decorators) and automated test-to-source mapping.
- **Integrated**: Standard file-level detection and execution support with reliable test generation.
- **Experimental**: Basic generation capabilities with manual verification recommended.

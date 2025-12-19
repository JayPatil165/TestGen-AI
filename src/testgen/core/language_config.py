"""
Language Configuration System for TestGen AI.

Defines language-specific settings, patterns, and conventions.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class Language(Enum):
    """Supported languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    CSHARP = "csharp"
    RUBY = "ruby"
    RUST = "rust"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    CPP = "cpp"
    C = "c"
    HTML = "html"
    CSS = "css"
    UNKNOWN = "unknown"



@dataclass
class LanguageConfig:
    """Configuration for a specific programming language."""
    
    name: str
    language: Language
    file_extensions: List[str]
    test_file_patterns: List[str]
    test_frameworks: List[str]
    default_framework: str
    comment_style: str  # "//", "#", "/**/", etc.
    import_keyword: str  # "import", "require", "using", etc.
    test_directory: str
    assertion_style: str
    
    # Code patterns
    function_pattern: str  # How functions are defined
    class_pattern: str
    test_function_prefix: str
    test_class_prefix: str
    
    # File naming
    test_file_prefix: str  # "test_", "", etc.
    test_file_suffix: str  # ".test", "_test", "Test", etc.
    
    # Tree-sitter
    tree_sitter_language: str  # Tree-sitter language name


# Language configurations
LANGUAGE_CONFIGS = {
    Language.PYTHON: LanguageConfig(
        name="Python",
        language=Language.PYTHON,
        file_extensions=[".py", ".pyw"],
        test_file_patterns=["test_*.py", "*_test.py"],
        test_frameworks=["pytest", "unittest", "nose"],
        default_framework="pytest",
        comment_style="#",
        import_keyword="import",
        test_directory="tests",
        assertion_style="assert",
        function_pattern="def",
        class_pattern="class",
        test_function_prefix="test_",
        test_class_prefix="Test",
        test_file_prefix="test_",
        test_file_suffix="",
        tree_sitter_language="python"
    ),
    
    Language.JAVASCRIPT: LanguageConfig(
        name="JavaScript",
        language=Language.JAVASCRIPT,
        file_extensions=[".js", ".jsx", ".mjs"],
        test_file_patterns=["*.test.js", "*.spec.js", "**/__tests__/**/*.js"],
        test_frameworks=["jest", "mocha", "jasmine", "vitest"],
        default_framework="jest",
        comment_style="//",
        import_keyword="import",
        test_directory="tests",
        assertion_style="expect",
        function_pattern="function",
        class_pattern="class",
        test_function_prefix="test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix=".test",
        tree_sitter_language="javascript"
    ),
    
    Language.TYPESCRIPT: LanguageConfig(
        name="TypeScript",
        language=Language.TYPESCRIPT,
        file_extensions=[".ts", ".tsx"],
        test_file_patterns=["*.test.ts", "*.spec.ts", "**/__tests__/**/*.ts"],
        test_frameworks=["jest", "mocha", "vitest"],
        default_framework="jest",
        comment_style="//",
        import_keyword="import",
        test_directory="tests",
        assertion_style="expect",
        function_pattern="function",
        class_pattern="class",
        test_function_prefix="test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix=".test",
        tree_sitter_language="typescript"
    ),
    
    Language.JAVA: LanguageConfig(
        name="Java",
        language=Language.JAVA,
        file_extensions=[".java"],
        test_file_patterns=["*Test.java", "*Tests.java"],
        test_frameworks=["junit", "testng"],
        default_framework="junit",
        comment_style="//",
        import_keyword="import",
        test_directory="src/test/java",
        assertion_style="assertEquals",
        function_pattern="public|private|protected",
        class_pattern="class",
        test_function_prefix="test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix="Test",
        tree_sitter_language="java"
    ),
    
    Language.GO: LanguageConfig(
        name="Go",
        language=Language.GO,
        file_extensions=[".go"],
        test_file_patterns=["*_test.go"],
        test_frameworks=["testing"],
        default_framework="testing",
        comment_style="//",
        import_keyword="import",
        test_directory=".",  # Go tests in same directory
        assertion_style="if",
        function_pattern="func",
        class_pattern="type",
        test_function_prefix="Test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix="_test",
        tree_sitter_language="go"
    ),
    
    Language.CSHARP: LanguageConfig(
        name="C#",
        language=Language.CSHARP,
        file_extensions=[".cs"],
        test_file_patterns=["*Tests.cs", "*Test.cs"],
        test_frameworks=["nunit", "xunit", "mstest"],
        default_framework="nunit",
        comment_style="//",
        import_keyword="using",
        test_directory="tests",
        assertion_style="Assert",
        function_pattern="public|private|protected",
        class_pattern="class",
        test_function_prefix="Test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix="Tests",
        tree_sitter_language="c_sharp"
    ),
    
    Language.RUBY: LanguageConfig(
        name="Ruby",
        language=Language.RUBY,
        file_extensions=[".rb"],
        test_file_patterns=["*_spec.rb", "test_*.rb"],
        test_frameworks=["rspec", "minitest"],
        default_framework="rspec",
        comment_style="#",
        import_keyword="require",
        test_directory="spec",
        assertion_style="expect",
        function_pattern="def",
        class_pattern="class",
        test_function_prefix="test_",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix="_spec",
        tree_sitter_language="ruby"
    ),
    
    Language.RUST: LanguageConfig(
        name="Rust",
        language=Language.RUST,
        file_extensions=[".rs"],
        test_file_patterns=["*_test.rs", "tests/*.rs"],
        test_frameworks=["cargo"],
        default_framework="cargo",
        comment_style="//",
        import_keyword="use",
        test_directory="tests",
        assertion_style="assert",
        function_pattern="fn",
        class_pattern="struct",
        test_function_prefix="test_",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix="_test",
        tree_sitter_language="rust"
    ),
    
    Language.PHP: LanguageConfig(
        name="PHP",
        language=Language.PHP,
        file_extensions=[".php"],
        test_file_patterns=["*Test.php"],
        test_frameworks=["phpunit"],
        default_framework="phpunit",
        comment_style="//",
        import_keyword="use",
        test_directory="tests",
        assertion_style="assertEquals",
        function_pattern="function",
        class_pattern="class",
        test_function_prefix="test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix="Test",
        tree_sitter_language="php"
    ),
    
    Language.SWIFT: LanguageConfig(
        name="Swift",
        language=Language.SWIFT,
        file_extensions=[".swift"],
        test_file_patterns=["*Tests.swift"],
        test_frameworks=["xctest"],
        default_framework="xctest",
        comment_style="//",
        import_keyword="import",
        test_directory="Tests",
        assertion_style="XCTAssert",
        function_pattern="func",
        class_pattern="class",
        test_function_prefix="test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix="Tests",
        tree_sitter_language="swift"
    ),
    
    Language.KOTLIN: LanguageConfig(
        name="Kotlin",
        language=Language.KOTLIN,
        file_extensions=[".kt", ".kts"],
        test_file_patterns=["*Test.kt"],
        test_frameworks=["junit", "kotlintest"],
        default_framework="junit",
        comment_style="//",
        import_keyword="import",
        test_directory="src/test/kotlin",
        assertion_style="assertEquals",
        function_pattern="fun",
        class_pattern="class",
        test_function_prefix="test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix="Test",
        tree_sitter_language="kotlin"
    ),
    
    Language.CPP: LanguageConfig(
        name="C++",
        language=Language.CPP,
        file_extensions=[".cpp", ".cc", ".cxx", ".hpp", ".h"],
        test_file_patterns=["*_test.cpp", "*Test.cpp"],
        test_frameworks=["gtest", "catch2", "boost"],
        default_framework="gtest",
        comment_style="//",
        import_keyword="#include",
        test_directory="tests",
        assertion_style="ASSERT",
        function_pattern="void|int|auto",
        class_pattern="class",
        test_function_prefix="TEST",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix="_test",
        tree_sitter_language="cpp"
    ),
    
    Language.HTML: LanguageConfig(
        name="HTML",
        language=Language.HTML,
        file_extensions=[".html", ".htm"],
        test_file_patterns=["*.test.html", "*.spec.html"],
        test_frameworks=["playwright", "puppeteer", "selenium"],
        default_framework="playwright",
        comment_style="<!--",
        import_keyword="<script",
        test_directory="tests",
        assertion_style="expect",
        function_pattern="function",
        class_pattern="class",
        test_function_prefix="test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix=".test",
        tree_sitter_language="html"
    ),
    
    Language.CSS: LanguageConfig(
        name="CSS",
        language=Language.CSS,
        file_extensions=[".css", ".scss", ".sass", ".less"],
        test_file_patterns=["*.test.css", "*.spec.css"],
        test_frameworks=["stylelint", "backstopjs"],
        default_framework="stylelint",
        comment_style="/*",
        import_keyword="@import",
        test_directory="tests",
        assertion_style="toMatchSnapshot",
        function_pattern="@mixin",
        class_pattern=".",
        test_function_prefix="test",
        test_class_prefix="",
        test_file_prefix="",
        test_file_suffix=".test",
        tree_sitter_language="css"
    ),
}



def get_language_config(language: Language) -> LanguageConfig:
    """
    Get configuration for a language.
    
    Args:
        language: Language enum
        
    Returns:
        LanguageConfig for the language
    """
    return LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS[Language.PYTHON])


def get_supported_languages() -> List[str]:
    """Get list of all supported languages."""
    return [lang.value for lang in LANGUAGE_CONFIGS.keys() if lang != Language.UNKNOWN]


def get_language_by_extension(ext: str) -> Language:
    """
    Get language from file extension.
    
    Args:
        ext: File extension (with or without dot)
        
    Returns:
        Language enum
    """
    if not ext.startswith('.'):
        ext = f'.{ext}'
    
    for lang, config in LANGUAGE_CONFIGS.items():
        if ext in config.file_extensions:
            return lang
    
    return Language.UNKNOWN

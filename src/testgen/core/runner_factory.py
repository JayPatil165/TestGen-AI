"""
Test Runner Factory for TestGen AI.

Automatically creates the appropriate test runner based on project language.
"""

from pathlib import Path
from typing import Optional

from .base_runner import BaseTestRunner
from .language_config import Language
from .language_detector import LanguageDetector, TestFramework
from .python_runner import PythonTestRunner
from .javascript_runner import JavaScriptTestRunner
from .java_runner import JavaTestRunner
from .go_runner import GoTestRunner
from .csharp_runner import CSharpTestRunner
from .ruby_runner import RubyTestRunner
from .rust_runner import RustTestRunner
from .php_runner import PHPTestRunner
from .swift_runner import SwiftTestRunner
from .kotlin_runner import KotlinTestRunner
from .cpp_runner import CppTestRunner
from .html_runner import HTMLTestRunner
from .css_runner import CSSTestRunner




class TestRunnerFactory:
    """
    Factory for creating language-specific test runners.
    
    Automatically detects project language and returns the appropriate runner.
    
    Example:
        >>> factory = TestRunnerFactory()
        >>> runner = factory.create_runner("./my-project")
        >>> results = runner.run_tests("tests/")
    """
    
    def __init__(self):
        """Initialize factory."""
        self.detector = LanguageDetector()
    
    def create_runner(
        self,
        project_dir: str,
        language: Optional[Language] = None,
        verbose: bool = False
    ) -> BaseTestRunner:
        """
        Create appropriate test runner for project.
        
        Args:
            project_dir: Project directory path
            language: Force specific language (optional, will auto-detect)
            verbose: Enable verbose output
            
        Returns:
            Language-specific test runner
            
        Example:
            >>> factory = TestRunnerFactory()
            >>> runner = factory.create_runner("./my-python-project")
            >>> # Returns PythonTestRunner
        """
        # Auto-detect language if not provided
        if language is None:
            language = self.detector.detect_language(project_dir)
        
        # Create appropriate runner
        if language == Language.PYTHON:
            return PythonTestRunner(verbose=verbose)
        
        elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            return JavaScriptTestRunner(verbose=verbose)
        
        elif language == Language.JAVA:
            return JavaTestRunner(verbose=verbose)
        
        elif language == Language.GO:
            return GoTestRunner(verbose=verbose)
        
        elif language == Language.CSHARP:
            return CSharpTestRunner(verbose=verbose)
        
        elif language == Language.RUBY:
            return RubyTestRunner(verbose=verbose)
        
        elif language == Language.RUST:
            return RustTestRunner(verbose=verbose)
        
        elif language == Language.PHP:
            return PHPTestRunner(verbose=verbose)
        
        elif language == Language.SWIFT:
            return SwiftTestRunner(verbose=verbose)
        
        elif language == Language.KOTLIN:
            return KotlinTestRunner(verbose=verbose)
        
        elif language == Language.CPP:
            return CppTestRunner(verbose=verbose)
        
        elif language == Language.HTML:
            return HTMLTestRunner(verbose=verbose)
        
        elif language == Language.CSS:
            return CSSTestRunner(verbose=verbose)
        
        else:
            # Default to Python for unknown languages
            print(f"Warning: Unknown language '{language}', defaulting to Python runner")
            return PythonTestRunner(verbose=verbose)
    
    def get_supported_languages(self) -> list:
        """
        Get list of currently supported languages.
        
        Returns:
            List of supported language names
        """
        return [
            Language.PYTHON.value,
            Language.JAVASCRIPT.value,
            Language.TYPESCRIPT.value,
            Language.JAVA.value,
            Language.GO.value,
            Language.CSHARP.value,
            Language.RUBY.value,
            Language.RUST.value,
            Language.PHP.value,
            Language.SWIFT.value,
            Language.KOTLIN.value,
            Language.CPP.value,
            Language.HTML.value,
            Language.CSS.value,
        ]
    
    def get_project_info(self, project_dir: str) -> dict:
        """
        Get complete project and runner information.
        
        Args:
            project_dir: Project directory
            
        Returns:
            Dictionary with language, framework, and runner info
        """
        language = self.detector.detect_language(project_dir)
        framework = self.detector.detect_test_framework(project_dir, language)
        
        try:
            runner = self.create_runner(project_dir, language)
            runner_available = True
            runner_class = runner.__class__.__name__
        except NotImplementedError:
            runner_available = False
            runner_class = None
        
        return {
            "language": language.value,
            "test_framework": framework.value,
            "runner_available": runner_available,
            "runner_class": runner_class,
            "project_dir": project_dir,
            "supported_languages": self.get_supported_languages()
        }


# Convenience function for quick access
def create_test_runner(
    project_dir: str,
    verbose: bool = False
) -> BaseTestRunner:
    """
    Quick function to create test runner.
    
    Args:
        project_dir: Project directory
        verbose: Enable verbose output
        
    Returns:
        Appropriate test runner
        
    Example:
        >>> from testgen.core.runner_factory import create_test_runner
        >>> runner = create_test_runner("./my-project")
        >>> results = runner.run_tests("tests/")
    """
    factory = TestRunnerFactory()
    return factory.create_runner(project_dir, verbose=verbose)

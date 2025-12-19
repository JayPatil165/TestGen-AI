"""
Base Test Runner Interface for TestGen AI.

Abstract base class for language-specific test runners.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class TestResult:
    """Single test result (language-agnostic)."""
    
    name: str
    status: str  # passed, failed, skipped, error
    duration: float = 0.0
    message: Optional[str] = None
    traceback: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    
    @property
    def passed(self) -> bool:
        """Check if test passed."""
        return self.status == "passed"


@dataclass
class TestResults:
    """
    Test execution results (language-agnostic).
    
    Attributes:
        tests: List of test results
        total: Total number of tests
        passed: Number of passed tests
        failed: Number of failed tests
        skipped: Number of skipped tests
        errors: Number of errors
        duration: Total execution time
        language: Programming language
        framework: Test framework used
    """
    
    tests: List[TestResult] = None
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    language: str = "unknown"
    framework: str = "unknown"
    
    def __post_init__(self):
        if self.tests is None:
            self.tests = []
    
    @property
    def success(self) -> bool:
        """Check if all tests passed."""
        return self.failed == 0 and self.errors == 0
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    def __str__(self) -> str:
        """String representation."""
        status = "[PASS]" if self.success else "[FAIL]"
        return (
            f"{status} {self.passed}/{self.total} passed "
            f"({self.pass_rate:.1f}%) in {self.duration:.2f}s "
            f"[{self.language}/{self.framework}]"
        )


class BaseTestRunner(ABC):
    """
    Abstract base class for test runners.
    
    All language-specific runners must inherit from this class.
    Provides a common interface for running tests across different languages.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize test runner.
        
        Args:
            verbose: Print verbose output
        """
        self.verbose = verbose
    
    @abstractmethod
    def run_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None,
        **kwargs
    ) -> TestResults:
        """
        Run tests in directory.
        
        Args:
            test_dir: Directory containing tests
            pattern: File/test pattern to match (optional)
            **kwargs: Additional runner-specific arguments
            
        Returns:
            TestResults with execution results
        """
        pass
    
    @abstractmethod
    def discover_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> List[Path]:
        """
        Discover test files matching pattern.
        
        Args:
            test_dir: Directory to search
            pattern: File pattern to match
            
        Returns:
            List of test file paths
        """
        pass
    
    @abstractmethod
    def count_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> int:
        """
        Count total tests before execution.
        
        Args:
            test_dir: Directory containing tests
            pattern: File pattern to match
            
        Returns:
            Total number of tests found
        """
        pass
    
    @abstractmethod
    def build_command(
        self,
        test_dir: str,
        pattern: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Build test execution command.
        
        Args:
            test_dir: Test directory
            pattern: Test pattern
            **kwargs: Additional arguments
            
        Returns:
            Command as list of strings
        """
        pass
    
    @abstractmethod
    def validate_test_file(self, test_file: str) -> bool:
        """
        Validate test file syntax and structure.
        
        Args:
            test_file: Path to test file
            
        Returns:
            True if valid
        """
        pass
    
    def get_language(self) -> str:
        """
        Get language name.
        
        Returns:
            Language name (e.g., 'python', 'javascript')
        """
        return "unknown"
    
    def get_framework(self) -> str:
        """
        Get test framework name.
        
        Returns:
            Framework name (e.g., 'pytest', 'jest')
        """
        return "unknown"
    
    def get_test_patterns(self) -> List[str]:
        """
        Get default test file patterns for this language.
        
        Returns:
            List of glob patterns
        """
        return []
    
    def supports_coverage(self) -> bool:
        """
        Check if runner supports coverage reporting.
        
        Returns:
            True if coverage is supported
        """
        return False
    
    def supports_parallel(self) -> bool:
        """
        Check if runner supports parallel execution.
        
        Returns:
            True if parallel execution is supported
        """
        return False
    
    def get_test_info(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed test information.
        
        Args:
            test_dir: Test directory
            pattern: File pattern
            
        Returns:
            Dictionary with test info
        """
        test_files = self.discover_tests(test_dir, pattern)
        test_count = self.count_tests(test_dir, pattern)
        
        return {
            "language": self.get_language(),
            "framework": self.get_framework(),
            "test_files": len(test_files),
            "test_count": test_count,
            "files": [str(f) for f in test_files],
            "pattern": pattern or "default",
            "directory": test_dir,
            "supports_coverage": self.supports_coverage(),
            "supports_parallel": self.supports_parallel(),
        }

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
    """A standardized container for a single test's execution metadata.

    This model is language-agnostic and provides a unified format for
    representing passes, failures, and errors across different frameworks.

    Attributes:
        name (str): The unique identifier or name of the test function/case.
        status (str): The execution outcome (e.g., 'passed', 'failed', 'skipped', 'error').
        duration (float): Time taken to execute the test in seconds. Defaults to 0.0.
        message (Optional[str]): A descriptive failure or error message.
        traceback (Optional[str]): The detailed stack trace for failures or errors.
        file_path (Optional[str]): Path to the file containing this test.
        line_number (Optional[int]): The specific line where the test is defined.
    """
    
    @property
    def passed(self) -> bool:
        """Check if test passed."""
        return self.status == "passed"


@dataclass
class TestResults:
    """Aggregated execution summary for a set of tests.

    This model provides both high-level statistics (counts, duration, pass rate)
     and granular details for individual test cases.

    Attributes:
        tests (List[TestResult]): A collection of individual test outcomes.
        total (int): The total number of tests attempted.
        passed (int): Count of tests that successfully completed.
        failed (int): Count of tests that failed their assertions.
        skipped (int): Count of tests that were explicitly bypassed.
        errors (int): Count of tests that encountered unexpected execution errors.
        duration (float): The total wall-clock time for the test suite in seconds.
        language (str): The programming language of the tested modules.
        framework (str): The name of the testing framework used (e.g., 'pytest').
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
    """Abstract foundational component for all language-specific test runners.

    The BaseTestRunner defines the contract for discovering, counting, and
    executing tests. It ensures a consistent interface across the system,
    allowing the WorkflowManager to interact with any language runner
    identically.

    Inherit from this class to implement a new language runner.
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize the base runner with common execution state.

        Args:
            verbose (bool): If True, enables detailed console output
                during the testing lifecycle.
        """
        self.verbose = verbose
    
    @abstractmethod
    def run_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None,
        **kwargs
    ) -> TestResults:
        """Execute the tests within the specified directory.

        Args:
            test_dir (str): Path to the directory containing test files.
            pattern (Optional[str]): A glob pattern to filter test files.
            **kwargs: Implementation-specific flags (e.g., json_report).

        Returns:
            TestResults: Aggregated outcome of the test run.
        """
        pass
    
    @abstractmethod
    def discover_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> List[Path]:
        """Locate all relevant test files within a directory.

        Args:
            test_dir (str): Base directory for discovery.
            pattern (Optional[str]): Filtering pattern for filenames.

        Returns:
            List[Path]: A list of absolute paths to the identified test files.
        """
        pass
    
    @abstractmethod
    def count_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> int:
        """Estimate the total number of test cases without full execution.

        Args:
            test_dir (str): Directory to scan.
            pattern (Optional[str]): Filtering pattern.

        Returns:
            int: The total count of test functions/checks detected.
        """
        pass
    
    @abstractmethod
    def build_command(
        self,
        test_dir: str,
        pattern: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """Generate the shell command for executing the test suite.

        Args:
            test_dir (str): Target directory.
            pattern (Optional[str]): Active filter pattern.
            **kwargs: Extra arguments for the CLI tool.

        Returns:
            List[str]: The complete command as a sequence of strings.
        """
        pass
    
    @abstractmethod
    def validate_test_file(self, test_file: str) -> bool:
        """Perform static validation on a generated test file.

        Args:
            test_file (str): Path to the file to check.

        Returns:
            bool: True if the file meets the language's syntactic requirements.
        """
        pass
    
    def get_language(self) -> str:
        """Return the lowercase name of the supported language.

        Returns:
            str: Identifier like 'python', 'javascript', etc.
        """
        return "unknown"
    
    def get_framework(self) -> str:
        """Return the name of the testing framework being utilized.

        Returns:
            str: Framework name like 'pytest' or 'jest'.
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
        """Indicate if the runner can provide code coverage metrics.

        Returns:
            bool: True if coverage data is available.
        """
        return False
    
    def supports_parallel(self) -> bool:
        """Indicate if the runner supports concurrent test execution.

        Returns:
            bool: True if parallel mode can be enabled.
        """
        return False
    
    def get_test_info(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """Aggregate high-level diagnostic information about the test environment.

        Args:
            test_dir (str): The directory being analyzed.
            pattern (Optional[str]): Active filtering pattern.

        Returns:
            Dict[str, Any]: A consolidated dictionary of runner capabilities
                and discovery results.
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

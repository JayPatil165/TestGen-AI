"""
Universal Test Result Data Models using Pydantic V2.

Comprehensive models for test results across ALL 14 languages.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TestStatus(str, Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestType(str, Enum):
    """Type of test."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    UI = "ui"
    PERFORMANCE = "performance"
    API = "api"
    UNKNOWN = "unknown"



class Language(str, Enum):
    """Supported programming languages."""
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
    CPP = "cpp"
    HTML = "html"
    CSS = "css"
    UNKNOWN = "unknown"


class TestFramework(str, Enum):
    """Supported test frameworks."""
    PYTEST = "pytest"
    JEST = "jest"
    JUNIT = "junit"
    GO_TESTING = "testing"
    NUNIT = "nunit"
    RSPEC = "rspec"
    CARGO = "cargo"
    PHPUNIT = "phpunit"
    XCTEST = "xctest"
    GTEST = "gtest"
    PLAYWRIGHT = "playwright"
    UNKNOWN = "unknown"


class ErrorInfo(BaseModel):
    """Error information for failed tests."""
    message: str
    type: Optional[str] = None
    traceback: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)


class TestResult(BaseModel):
    """Individual test result."""
    name: str
    status: TestStatus
    duration: float = 0.0
    error: Optional[ErrorInfo] = None
    language: Language = Language.UNKNOWN
    framework: TestFramework = TestFramework.UNKNOWN
    
    @property
    def passed(self) -> bool:
        return self.status == TestStatus.PASSED
    
    @property
    def failed(self) -> bool:
        return self.status == TestStatus.FAILED
    
    @property
    def skipped(self) -> bool:
        return self.status == TestStatus.SKIPPED
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)
    
    model_config = ConfigDict(use_enum_values=True)


class TestSuite(BaseModel):
    """Collection of tests from a file."""
    name: str
    file_path: str
    tests: List[TestResult] = []
    total_duration: float = 0.0
    language: Language = Language.UNKNOWN
    framework: TestFramework = TestFramework.UNKNOWN
    
    @property
    def total_tests(self) -> int:
        return len(self.tests)
    
    @property
    def passed_tests(self) -> int:
        return sum(1 for t in self.tests if t.passed)
    
    @property
    def failed_tests(self) -> int:
        return sum(1 for t in self.tests if t.failed)
    
    @property
    def skipped_tests(self) -> int:
        return sum(1 for t in self.tests if t.skipped)
    
    @property
    def pass_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    model_config = ConfigDict(use_enum_values=True)


class ExecutionSummary(BaseModel):
    """Summary of test execution."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    language: Language = Language.UNKNOWN
    framework: TestFramework = TestFramework.UNKNOWN
    suites: List[TestSuite] = []
    
    @property
    def success(self) -> bool:
        return self.failed == 0 and self.errors == 0
    
    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    def get_summary_text(self) -> str:
        status = "✅ PASSED" if self.success else "❌ FAILED"
        return (
            f"{status} - {self.language}/{self.framework}\n"
            f"  Total: {self.total}, Passed: {self.passed}, "
            f"Failed: {self.failed}, Skipped: {self.skipped}\n"
            f"  Duration: {self.duration:.2f}s, Pass Rate: {self.pass_rate:.1f}%"
        )
    
    model_config = ConfigDict(use_enum_values=True)


# Utility functions
def create_test_result_from_dict(data: Dict[str, Any]) -> TestResult:
    return TestResult(**data)


def create_test_suite_from_results(
    name: str,
    file_path: str,
    results: List[TestResult],
    language: Language = Language.UNKNOWN,
    framework: TestFramework = TestFramework.UNKNOWN
) -> TestSuite:
    return TestSuite(
        name=name,
        file_path=file_path,
        tests=results,
        language=language,
        framework=framework
    )


def create_execution_summary_from_suites(
    suites: List[TestSuite],
    language: Language = Language.UNKNOWN,
    framework: TestFramework = TestFramework.UNKNOWN
) -> ExecutionSummary:
    total = sum(s.total_tests for s in suites)
    passed = sum(s.passed_tests for s in suites)
    failed = sum(s.failed_tests for s in suites)
    skipped = sum(s.skipped_tests for s in suites)
    duration = sum(s.total_duration for s in suites)
    
    return ExecutionSummary(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration=duration,
        language=language,
        framework=framework,
        suites=suites
    )

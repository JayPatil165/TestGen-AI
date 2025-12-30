"""
Universal Failure Analyzer for TestGen AI.

Analyze test failures and extract patterns across ALL 14 languages.
"""

from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass
from collections import Counter
import re

from .result_models import TestResult, TestSuite, ExecutionSummary, Language, TestFramework, ErrorInfo


class FailureType(str, Enum):
    """Types of test failures."""
    ASSERTION = "assertion"
    EXCEPTION = "exception"
    TIMEOUT = "timeout"
    COMPILATION = "compilation"
    IMPORT_ERROR = "import_error"
    RUNTIME_ERROR = "runtime_error"
    NETWORK_ERROR = "network_error"
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_ERROR = "permission_error"
    MEMORY_ERROR = "memory_error"
    UNKNOWN = "unknown"


@dataclass
class FailurePattern:
    """Identified failure pattern."""
    type: FailureType
    message_pattern: str
    count: int
    examples: List[str]
    affected_tests: List[str]


@dataclass
class FailureAnalysis:
    """Complete failure analysis results."""
    total_failures: int
    failure_types: Dict[FailureType, int]
    common_patterns: List[FailurePattern]
    most_common_errors: List[Tuple[str, int]]
    flaky_candidates: List[str]  # Tests that might be flaky
    language: Language
    framework: TestFramework


class FailureAnalyzer:
    """
    Analyze test failures across ALL 14 programming languages.
    
    Identifies failure types, extracts patterns, and provides insights.
    """
    
    # Language-specific error patterns
    ERROR_PATTERNS = {
        # Assertion errors
        "assertion": [
            r"AssertionError",
            r"assert.*failed",
            r"Expected.*but got",
            r"assertion `.*` failed",  # Rust
            r"FAIL:",  # Go
            r"Expected:.*Actual:",  # JUnit
            r"to equal",  # Jest
            r"should.*but",  # RSpec
        ],
        
        # Timeout errors
        "timeout": [
            r"TimeoutError",
            r"timeout",
            r"timed out",
            r"Timeout exceeded",
            r"Test timeout",
        ],
        
        # Import/Module errors
        "import_error": [
            r"ImportError",
            r"ModuleNotFoundError",
            r"cannot find module",  # JavaScript
            r"package.*does not exist",  # Java
            r"use of undeclared",  # Go
            r"cannot find name",  # TypeScript
        ],
        
        # Runtime errors
        "runtime_error": [
            r"RuntimeError",
            r"NullPointerException",  # Java
            r"nil pointer",  # Go
            r"null is not an object",  # JavaScript
            r"Cannot read property.*of null",
            r"undefined is not",
        ],
        
        # Network errors
        "network_error": [
            r"ConnectionError",
            r"NetworkError",
            r"ECONNREFUSED",
            r"Failed to fetch",
            r"Connection refused",
        ],
        
        # File errors
        "file_not_found": [
            r"FileNotFoundError",
            r"No such file",
            r"ENOENT",
            r"File not found",
        ],
        
        # Memory errors
        "memory_error": [
            r"MemoryError",
            r"OutOfMemoryError",
            r"heap out of memory",
        ],
        
        # Permission errors
        "permission_error": [
            r"PermissionError",
            r"Permission denied",
            r"EACCES",
        ],
    }
    
    def __init__(self, language: Language = Language.UNKNOWN, framework: TestFramework = TestFramework.UNKNOWN):
        """
        Initialize failure analyzer.
        
        Args:
            language: Programming language
            framework: Test framework
        """
        self.language = language
        self.framework = framework
        self.failed_tests: List[Tuple[TestResult, str]] = []  # (test, suite_name)
    
    def add_test(self, test: TestResult, suite_name: str = "") -> None:
        """Add a failed test for analysis."""
        if test.failed:
            self.failed_tests.append((test, suite_name))
    
    def add_suite(self, suite: TestSuite) -> None:
        """Add all failed tests from a suite."""
        for test in suite.tests:
            if test.failed:
                self.add_test(test, suite.name)
    
    def add_summary(self, summary: ExecutionSummary) -> None:
        """Add all failed tests from an execution summary."""
        for suite in summary.suites:
            self.add_suite(suite)
    
    def classify_failure(self, error_message: str) -> FailureType:
        """
        Classify failure type based on error message.
        
        Args:
            error_message: Error message from test failure
            
        Returns:
            Classified failure type
        """
        if not error_message:
            return FailureType.UNKNOWN
        
        message_lower = error_message.lower()
        
        # Check each pattern category
        for failure_type, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    return FailureType(failure_type)
        
        # Default to assertion if contains "assert" or "expect"
        if "assert" in message_lower or "expect" in message_lower:
            return FailureType.ASSERTION
        
        # Check for exception keywords
        if "exception" in message_lower or "error" in message_lower:
            return FailureType.EXCEPTION
        
        return FailureType.UNKNOWN
    
    def count_failure_types(self) -> Dict[FailureType, int]:
        """
        Count failures by type.
        
        Returns:
            Dictionary mapping failure type to count
        """
        counts = {ftype: 0 for ftype in FailureType}
        
        for test, _ in self.failed_tests:
            if test.error and test.error.message:
                ftype = self.classify_failure(test.error.message)
                counts[ftype] += 1
        
        return counts
    
    def extract_error_patterns(self, min_occurrences: int = 2) -> List[FailurePattern]:
        """
        Extract common error patterns.
        
        Args:
            min_occurrences: Minimum occurrences to be considered a pattern
            
        Returns:
            List of identified patterns
        """
        # Group errors by type and message similarity
        error_groups: Dict[str, List[Tuple[TestResult, str]]] = {}
        
        for test, suite_name in self.failed_tests:
            if not test.error or not test.error.message:
                continue
            
            # Normalize error message for pattern matching
            normalized = self._normalize_error_message(test.error.message)
            
            if normalized not in error_groups:
                error_groups[normalized] = []
            
            error_groups[normalized].append((test, suite_name))
        
        # Create patterns from groups with enough occurrences
        patterns = []
        for normalized_msg, tests_with_suite in error_groups.items():
            if len(tests_with_suite) >= min_occurrences:
                test_examples = tests_with_suite[:3]  # First 3 examples
                
                # Classify failure type
                ftype = self.classify_failure(test_examples[0][0].error.message)
                
                pattern = FailurePattern(
                    type=ftype,
                    message_pattern=normalized_msg,
                    count=len(tests_with_suite),
                    examples=[t.error.message for t, _ in test_examples],
                    affected_tests=[f"{t.name} ({s})" for t, s in tests_with_suite]
                )
                patterns.append(pattern)
        
        # Sort by count (most common first)
        return sorted(patterns, key=lambda p: p.count, reverse=True)
    
    def _normalize_error_message(self, message: str) -> str:
        """Normalize error message for pattern matching."""
        # Remove specific values/numbers but keep structure
        normalized = message
        
        # Remove line numbers
        normalized = re.sub(r'line \d+', 'line X', normalized)
        normalized = re.sub(r':\d+:', ':X:', normalized)
        
        # Remove specific values in quotes
        normalized = re.sub(r"'[^']*'", "'VALUE'", normalized)
        normalized = re.sub(r'"[^"]*"', '"VALUE"', normalized)
        
        # Remove numbers
        normalized = re.sub(r'\b\d+\b', 'N', normalized)
        
        # Remove file paths
        normalized = re.sub(r'/[\w/]+\.[\w]+', '/PATH/FILE', normalized)
        normalized = re.sub(r'\\[\w\\]+\.[\w]+', r'\\PATH\\FILE', normalized)
        
        return normalized
    
    def get_most_common_errors(self, n: int = 10) -> List[Tuple[str, int]]:
        """
        Get most common error messages.
        
        Args:
            n: Number of top errors to return
            
        Returns:
            List of (error_message, count) tuples
        """
        error_counter = Counter()
        
        for test, _ in self.failed_tests:
            if test.error and test.error.message:
                # Use normalized message for grouping
                normalized = self._normalize_error_message(test.error.message)
                error_counter[normalized] += 1
        
        return error_counter.most_common(n)
    
    def identify_flaky_tests(self) -> List[str]:
        """
        Identify potentially flaky tests.
        
        Flaky tests are identified by:
        - Timeout errors
        - Network errors
        - Intermittent errors
        
        Returns:
            List of potentially flaky test names
        """
        flaky = set()
        
        for test, suite_name in self.failed_tests:
            if not test.error:
                continue
            
            ftype = self.classify_failure(test.error.message)
            
            # Timeouts and network errors are often flaky
            if ftype in [FailureType.TIMEOUT, FailureType.NETWORK_ERROR]:
                flaky.add(f"{test.name} ({suite_name})")
        
        return sorted(list(flaky))
    
    def analyze(self) -> FailureAnalysis:
        """
        Perform complete failure analysis.
        
        Returns:
            Complete failure analysis results
        """
        return FailureAnalysis(
            total_failures=len(self.failed_tests),
            failure_types=self.count_failure_types(),
            common_patterns=self.extract_error_patterns(),
            most_common_errors=self.get_most_common_errors(),
            flaky_candidates=self.identify_flaky_tests(),
            language=self.language,
            framework=self.framework
        )
    
    def generate_failure_report(self) -> str:
        """
        Generate human-readable failure analysis report.
        
        Returns:
            Formatted failure report
        """
        analysis = self.analyze()
        
        report = []
        report.append("=" * 70)
        report.append("FAILURE ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"Language: {self.language.value}")
        report.append(f"Framework: {self.framework.value}")
        report.append("")
        
        report.append(f"Total Failures: {analysis.total_failures}")
        report.append("")
        
        # Failure types breakdown
        report.append("Failure Types:")
        for ftype, count in analysis.failure_types.items():
            if count > 0:
                percentage = (count / analysis.total_failures * 100) if analysis.total_failures > 0 else 0
                report.append(f"  {ftype.value:20}: {count:3} ({percentage:5.1f}%)")
        report.append("")
        
        # Common patterns
        if analysis.common_patterns:
            report.append("Common Error Patterns:")
            for i, pattern in enumerate(analysis.common_patterns[:5], 1):
                report.append(f"\n  {i}. {pattern.type.value.upper()} ({pattern.count} occurrences)")
                report.append(f"     Pattern: {pattern.message_pattern[:80]}...")
                report.append(f"     Example: {pattern.examples[0][:80]}...")
        report.append("")
        
        # Most common errors
        if analysis.most_common_errors:
            report.append("Most Common Errors:")
            for i, (error, count) in enumerate(analysis.most_common_errors[:5], 1):
                report.append(f"  {i}. ({count}x) {error[:60]}...")
        report.append("")
        
        # Flaky tests
        if analysis.flaky_candidates:
            report.append(f"⚠️  Potentially Flaky Tests ({len(analysis.flaky_candidates)}):")
            for test_name in analysis.flaky_candidates[:5]:
                report.append(f"  - {test_name}")
            if len(analysis.flaky_candidates) > 5:
                report.append(f"  ... and {len(analysis.flaky_candidates) - 5} more")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def get_failures_by_type(self, failure_type: FailureType) -> List[Tuple[TestResult, str]]:
        """
        Get all failures of a specific type.
        
        Args:
            failure_type: Type of failure to filter
            
        Returns:
            List of (test, suite_name) matching the type
        """
        matching = []
        
        for test, suite_name in self.failed_tests:
            if test.error and test.error.message:
                ftype = self.classify_failure(test.error.message)
                if ftype == failure_type:
                    matching.append((test, suite_name))
        
        return matching


# Utility functions

def quick_failure_analysis(summary: ExecutionSummary) -> Dict[str, any]:
    """
    Quick failure analysis from execution summary.
    
    Args:
        summary: Execution summary to analyze
        
    Returns:
        Basic failure analysis results
    """
    analyzer = FailureAnalyzer(summary.language, summary.framework)
    analyzer.add_summary(summary)
    
    analysis = analyzer.analyze()
    
    return {
        "total_failures": analysis.total_failures,
        "failure_types": {k.value: v for k, v in analysis.failure_types.items() if v > 0},
        "common_patterns_count": len(analysis.common_patterns),
        "flaky_test_count": len(analysis.flaky_candidates)
    }


def compare_failure_patterns(
    analyzer1: FailureAnalyzer,
    analyzer2: FailureAnalyzer
) -> Dict[str, any]:
    """
    Compare failure patterns between two test runs.
    
    Args:
        analyzer1: First analyzer (e.g., previous run)
        analyzer2: Second analyzer (e.g., current run)
        
    Returns:
        Comparison results
    """
    analysis1 = analyzer1.analyze()
    analysis2 = analyzer2.analyze()
    
    return {
        "failure_count_change": analysis2.total_failures - analysis1.total_failures,
        "new_failure_types": set(analysis2.failure_types.keys()) - set(analysis1.failure_types.keys()),
        "resolved_failure_types": set(analysis1.failure_types.keys()) - set(analysis2.failure_types.keys())
    }

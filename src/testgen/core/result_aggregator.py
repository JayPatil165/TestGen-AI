"""
Universal Test Result Aggregator for TestGen AI.

Combines and aggregates test results from multiple files/suites
across ALL 14 programming languages.
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta

from .result_models import (
    TestResult, TestSuite, ExecutionSummary,
    TestStatus, Language, TestFramework
)


class ResultAggregator:
    """
    Aggregate test results across multiple files and suites.
    
    Works for ALL 14 languages with consistent behavior.
    """
    
    def __init__(self, language: Language = Language.UNKNOWN, framework: TestFramework = TestFramework.UNKNOWN):
        """
        Initialize aggregator.
        
        Args:
            language: Programming language
            framework: Test framework
        """
        self.language = language
        self.framework = framework
        self.suites: List[TestSuite] = []
    
    def add_suite(self, suite: TestSuite) -> None:
        """Add a test suite to aggregation."""
        self.suites.append(suite)
    
    def add_suites(self, suites: List[TestSuite]) -> None:
        """Add multiple test suites."""
        self.suites.extend(suites)
    
    def combine_results(self) -> ExecutionSummary:
        """
        Combine all results into single ExecutionSummary.
        
        Returns:
            ExecutionSummary with aggregated statistics
        """
        if not self.suites:
            return ExecutionSummary(
                language=self.language,
                framework=self.framework
            )
        
        # Aggregate counts
        total = sum(s.total_tests for s in self.suites)
        passed = sum(s.passed_tests for s in self.suites)
        failed = sum(s.failed_tests for s in self.suites)
        skipped = sum(s.skipped_tests for s in self.suites)
        
        # Calculate total duration
        total_duration = self.calculate_total_duration()
        
        # Create summary
        summary = ExecutionSummary(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=total_duration,
            language=self.language,
            framework=self.framework,
            suites=self.suites
        )
        
        return summary
    
    def calculate_total_duration(self) -> float:
        """
        Calculate total execution duration across all suites.
        
        Returns:
            Total duration in seconds
        """
        return sum(s.total_duration for s in self.suites)
    
    def get_slowest_tests(self, n: int = 10) -> List[Tuple[TestResult, str]]:
        """
        Identify slowest tests across all suites.
        
        Args:
            n: Number of slowest tests to return
            
        Returns:
            List of tuples (test_result, suite_name)
        """
        all_tests_with_suite = []
        
        for suite in self.suites:
            for test in suite.tests:
                all_tests_with_suite.append((test, suite.name))
        
        # Sort by duration (descending)
        sorted_tests = sorted(
            all_tests_with_suite,
            key=lambda x: x[0].duration,
            reverse=True
        )
        
        return sorted_tests[:n]
    
    def get_fastest_tests(self, n: int = 10) -> List[Tuple[TestResult, str]]:
        """
        Identify fastest tests across all suites.
        
        Args:
            n: Number of fastest tests to return
            
        Returns:
            List of tuples (test_result, suite_name)
        """
        all_tests_with_suite = []
        
        for suite in self.suites:
            for test in suite.tests:
                all_tests_with_suite.append((test, suite.name))
        
        # Sort by duration (ascending)
        sorted_tests = sorted(
            all_tests_with_suite,
            key=lambda x: x[0].duration
        )
        
        return sorted_tests[:n]
    
    def get_failed_tests(self) -> List[Tuple[TestResult, str]]:
        """
        Get all failed tests across all suites.
        
        Returns:
            List of tuples (failed_test, suite_name)
        """
        failed_tests = []
        
        for suite in self.suites:
            for test in suite.tests:
                if test.failed:
                    failed_tests.append((test, suite.name))
        
        return failed_tests
    
    def get_slowest_suites(self, n: int = 5) -> List[TestSuite]:
        """
        Identify slowest test suites.
        
        Args:
            n: Number of slowest suites to return
            
        Returns:
            List of slowest test suites
        """
        return sorted(self.suites, key=lambda s: s.total_duration, reverse=True)[:n]
    
    def get_suites_with_failures(self) -> List[TestSuite]:
        """
        Get all suites that have failed tests.
        
        Returns:
            List of suites with failures
        """
        return [s for s in self.suites if s.failed_tests > 0]
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get comprehensive statistics about aggregated results.
        
        Returns:
            Dictionary with detailed statistics
        """
        if not self.suites:
            return {
                "total_suites": 0,
                "total_tests": 0,
                "total_duration": 0.0
            }
        
        all_tests = []
        for suite in self.suites:
            all_tests.extend(suite.tests)
        
        durations = [t.duration for t in all_tests]
        
        stats = {
            "total_suites": len(self.suites),
            "total_tests": sum(s.total_tests for s in self.suites),
            "passed": sum(s.passed_tests for s in self.suites),
            "failed": sum(s.failed_tests for s in self.suites),
            "skipped": sum(s.skipped_tests for s in self.suites),
            "total_duration": self.calculate_total_duration(),
            "average_test_duration": sum(durations) / len(durations) if durations else 0,
            "min_test_duration": min(durations) if durations else 0,
            "max_test_duration": max(durations) if durations else 0,
            "suites_with_failures": len(self.get_suites_with_failures()),
            "slowest_suite": max(self.suites, key=lambda s: s.total_duration).name if self.suites else None,
            "fastest_suite": min(self.suites, key=lambda s: s.total_duration).name if self.suites else None
        }
        
        return stats
    
    def group_by_status(self) -> Dict[TestStatus, List[Tuple[TestResult, str]]]:
        """
        Group all tests by their status.
        
        Returns:
            Dictionary mapping status to list of (test, suite_name)
        """
        grouped = {
            TestStatus.PASSED: [],
            TestStatus.FAILED: [],
            TestStatus.SKIPPED: [],
            TestStatus.ERROR: []
        }
        
        for suite in self.suites:
            for test in suite.tests:
                if test.status in grouped:
                    grouped[test.status].append((test, suite.name))
        
        return grouped
    
    def get_summary_report(self) -> str:
        """
        Generate human-readable summary report.
        
        Returns:
            Formatted summary text
        """
        summary = self.combine_results()
        stats = self.get_statistics()
        slowest = self.get_slowest_tests(5)
        
        report = []
        report.append("=" * 70)
        report.append("TEST RESULTS SUMMARY")
        report.append("=" * 70)
        report.append(f"Language: {self.language.value}")
        report.append(f"Framework: {self.framework.value}")
        report.append("")
        
        report.append("Overall Results:")
        report.append(f"  Total Tests: {summary.total}")
        report.append(f"  Passed: {summary.passed} ({summary.pass_rate:.1f}%)")
        report.append(f"  Failed: {summary.failed}")
        report.append(f"  Skipped: {summary.skipped}")
        report.append(f"  Duration: {summary.duration:.2f}s")
        report.append("")
        
        report.append("Test Suites:")
        report.append(f"  Total Suites: {stats['total_suites']}")
        report.append(f"  Suites with Failures: {stats['suites_with_failures']}")
        report.append("")
        
        report.append("Performance:")
        report.append(f"  Average Test Duration: {stats['average_test_duration']:.3f}s")
        report.append(f"  Fastest Test: {stats['min_test_duration']:.3f}s")
        report.append(f"  Slowest Test: {stats['max_test_duration']:.3f}s")
        report.append("")
        
        if slowest:
            report.append("Top 5 Slowest Tests:")
            for i, (test, suite) in enumerate(slowest, 1):
                report.append(f"  {i}. {test.name} ({suite}): {test.duration:.3f}s")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_to_dict(self) -> Dict[str, any]:
        """
        Export aggregated results to dictionary.
        
        Returns:
            Dictionary with all aggregated data
        """
        summary = self.combine_results()
        stats = self.get_statistics()
        
        return {
            "summary": summary.to_dict(),
            "statistics": stats,
            "slowest_tests": [
                {"name": test.name, "suite": suite, "duration": test.duration}
                for test, suite in self.get_slowest_tests(10)
            ],
            "failed_tests": [
                {"name": test.name, "suite": suite, "error": test.error.message if test.error else None}
                for test, suite in self.get_failed_tests()
            ],
            "suites": [
                {
                    "name": suite.name,
                    "total": suite.total_tests,
                    "passed": suite.passed_tests,
                    "failed": suite.failed_tests,
                    "duration": suite.total_duration
                }
                for suite in self.suites
            ]
        }


class MultiLanguageAggregator:
    """
    Aggregate results across MULTIPLE languages.
    
    Useful for polyglot projects with tests in multiple languages.
    """
    
    def __init__(self):
        """Initialize multi-language aggregator."""
        self.aggregators: Dict[Language, ResultAggregator] = {}
    
    def add_suite(self, suite: TestSuite) -> None:
        """Add a test suite (auto-grouped by language)."""
        if suite.language not in self.aggregators:
            self.aggregators[suite.language] = ResultAggregator(
                language=suite.language,
                framework=suite.framework
            )
        
        self.aggregators[suite.language].add_suite(suite)
    
    def get_language_summaries(self) -> Dict[Language, ExecutionSummary]:
        """
        Get summary for each language.
        
        Returns:
            Dictionary mapping language to its summary
        """
        return {
            lang: aggregator.combine_results()
            for lang, aggregator in self.aggregators.items()
        }
    
    def get_overall_summary(self) -> ExecutionSummary:
        """
        Get combined summary across all languages.
        
        Returns:
            Overall execution summary
        """
        all_suites = []
        for aggregator in self.aggregators.values():
            all_suites.extend(aggregator.suites)
        
        if not all_suites:
            return ExecutionSummary()
        
        # Combine all
        total = sum(s.total_tests for s in all_suites)
        passed = sum(s.passed_tests for s in all_suites)
        failed = sum(s.failed_tests for s in all_suites)
        skipped = sum(s.skipped_tests for s in all_suites)
        duration = sum(s.total_duration for s in all_suites)
        
        return ExecutionSummary(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            suites=all_suites,
            language=Language.UNKNOWN  # Multiple languages
        )
    
    def get_multi_language_report(self) -> str:
        """
        Generate report showing results per language.
        
        Returns:
            Formatted multi-language report
        """
        report = []
        report.append("=" * 70)
        report.append("MULTI-LANGUAGE TEST RESULTS")
        report.append("=" * 70)
        report.append("")
        
        for lang, summary in self.get_language_summaries().items():
            report.append(f"{lang.value.upper()}:")
            report.append(f"  Tests: {summary.total} (Passed: {summary.passed}, Failed: {summary.failed})")
            report.append(f"  Duration: {summary.duration:.2f}s")
            report.append(f"  Pass Rate: {summary.pass_rate:.1f}%")
            report.append("")
        
        overall = self.get_overall_summary()
        report.append("OVERALL:")
        report.append(f"  Total Tests: {overall.total}")
        report.append(f"  Passed: {overall.passed}")
        report.append(f"  Failed: {overall.failed}")
        report.append(f"  Duration: {overall.duration:.2f}s")
        report.append(f"  Pass Rate: {overall.pass_rate:.1f}%")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


# Utility functions

def aggregate_results_from_files(
    result_files: List[str],
    language: Language = Language.UNKNOWN,
    framework: TestFramework = TestFramework.UNKNOWN
) -> ExecutionSummary:
    """
    Aggregate results from multiple result files.
    
    Args:
        result_files: List of file paths containing test results
        language: Programming language
        framework: Test framework
        
    Returns:
        Aggregated execution summary
    """
    aggregator = ResultAggregator(language, framework)
    
    # In a real implementation, we'd load TestSuite objects from files
    # For now, this is a placeholder
    
    return aggregator.combine_results()


def merge_execution_summaries(summaries: List[ExecutionSummary]) -> ExecutionSummary:
    """
    Merge multiple ExecutionSummary objects into one.
    
    Args:
        summaries: List of execution summaries
        
    Returns:
        Merged execution summary
    """
    if not summaries:
        return ExecutionSummary()
    
    all_suites = []
    for summary in summaries:
        all_suites.extend(summary.suites)
    
    total = sum(s.total for s in summaries)
    passed = sum(s.passed for s in summaries)
    failed = sum(s.failed for s in summaries)
    skipped = sum(s.skipped for s in summaries)
    duration = sum(s.duration for s in summaries)
    
    return ExecutionSummary(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration=duration,
        suites=all_suites
    )

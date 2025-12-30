"""
Universal Performance Monitor for TestGen AI.

Track test performance and flag slow tests across ALL 14 languages.
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from .result_models import TestResult, TestSuite, ExecutionSummary, Language, TestFramework


class PerformanceLevel(str, Enum):
    """Performance level classification."""
    EXCELLENT = "excellent"  # < 0.1s
    GOOD = "good"           # 0.1s - 0.5s
    ACCEPTABLE = "acceptable"  # 0.5s - 1s
    WARNING = "warning"     # 1s - 5s
    CRITICAL = "critical"   # > 5s


@dataclass
class PerformanceThresholds:
    """
    Configurable performance thresholds.
    
    Supports different thresholds per language/framework.
    """
    excellent_max: float = 0.1      # < 0.1s = excellent
    good_max: float = 0.5           # 0.1s - 0.5s = good
    acceptable_max: float = 1.0     # 0.5s - 1s = acceptable
    warning_max: float = 5.0        # 1s - 5s = warning
    critical_min: float = 5.0       # > 5s = critical
    
    # Language-specific adjustments
    language_multipliers: Dict[Language, float] = None
    
    def __post_init__(self):
        """Initialize language multipliers."""
        if self.language_multipliers is None:
            # Some languages are naturally slower (e.g., interpreted vs compiled)
            self.language_multipliers = {
                Language.PYTHON: 1.0,
                Language.JAVASCRIPT: 1.0,
                Language.TYPESCRIPT: 1.0,
                Language.JAVA: 1.5,      # Slower startup
                Language.GO: 0.8,        # Usually faster
                Language.CSHARP: 1.5,    # Slower startup
                Language.RUBY: 1.2,      # Interpreted
                Language.RUST: 0.7,      # Very fast
                Language.PHP: 1.1,       # Interpreted
                Language.SWIFT: 1.0,
                Language.KOTLIN: 1.5,    # JVM startup
                Language.CPP: 0.6,       # Very fast
                Language.HTML: 1.0,
                Language.CSS: 1.0
            }
    
    def get_adjusted_threshold(self, threshold: float, language: Language) -> float:
        """Get language-adjusted threshold."""
        multiplier = self.language_multipliers.get(language, 1.0)
        return threshold * multiplier


@dataclass
class TestPerformanceInfo:
    """Detailed performance information for a test."""
    test: TestResult
    suite_name: str
    level: PerformanceLevel
    percentile: Optional[float] = None  # Percentile rank (0-100)
    times_slower_than_average: Optional[float] = None


class PerformanceMonitor:
    """
    Monitor and analyze test performance across ALL 14 languages.
    
    Tracks duration, flags slow tests, and provides performance analytics.
    """
    
    def __init__(
        self,
        thresholds: Optional[PerformanceThresholds] = None,
        language: Language = Language.UNKNOWN
    ):
        """
        Initialize performance monitor.
        
        Args:
            thresholds: Custom performance thresholds
            language: Programming language for threshold adjustment
        """
        self.thresholds = thresholds or PerformanceThresholds()
        self.language = language
        self.tests: List[Tuple[TestResult, str]] = []  # (test, suite_name)
    
    def add_test(self, test: TestResult, suite_name: str = "") -> None:
        """Add a test for performance tracking."""
        self.tests.append((test, suite_name))
    
    def add_suite(self, suite: TestSuite) -> None:
        """Add all tests from a suite."""
        for test in suite.tests:
            self.add_test(test, suite.name)
    
    def add_summary(self, summary: ExecutionSummary) -> None:
        """Add all tests from an execution summary."""
        for suite in summary.suites:
            self.add_suite(suite)
    
    def classify_performance(self, duration: float) -> PerformanceLevel:
        """
        Classify test performance based on duration.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            Performance level classification
        """
        # Adjust thresholds for language
        excellent = self.thresholds.get_adjusted_threshold(
            self.thresholds.excellent_max, self.language
        )
        good = self.thresholds.get_adjusted_threshold(
            self.thresholds.good_max, self.language
        )
        acceptable = self.thresholds.get_adjusted_threshold(
            self.thresholds.acceptable_max, self.language
        )
        warning = self.thresholds.get_adjusted_threshold(
            self.thresholds.warning_max, self.language
        )
        
        if duration < excellent:
            return PerformanceLevel.EXCELLENT
        elif duration < good:
            return PerformanceLevel.GOOD
        elif duration < acceptable:
            return PerformanceLevel.ACCEPTABLE
        elif duration < warning:
            return PerformanceLevel.WARNING
        else:
            return PerformanceLevel.CRITICAL
    
    def get_slow_tests(
        self,
        threshold: float = 1.0,
        level: Optional[PerformanceLevel] = None
    ) -> List[TestPerformanceInfo]:
        """
        Get tests slower than threshold or at specific performance level.
        
        Args:
            threshold: Duration threshold in seconds (default: 1.0s = warning)
            level: Optional specific performance level to filter
            
        Returns:
            List of slow test performance info
        """
        slow_tests = []
        avg_duration = self.get_average_duration()
        
        for test, suite_name in self.tests:
            perf_level = self.classify_performance(test.duration)
            
            # Filter by threshold or level
            if level:
                if perf_level != level:
                    continue
            else:
                if test.duration < threshold:
                    continue
            
            times_slower = test.duration / avg_duration if avg_duration > 0 else 1.0
            
            slow_tests.append(TestPerformanceInfo(
                test=test,
                suite_name=suite_name,
                level=perf_level,
                times_slower_than_average=times_slower
            ))
        
        return sorted(slow_tests, key=lambda x: x.test.duration, reverse=True)
    
    def get_critical_tests(self) -> List[TestPerformanceInfo]:
        """Get tests with critical performance (> 5s)."""
        return self.get_slow_tests(
            threshold=self.thresholds.critical_min,
            level=PerformanceLevel.CRITICAL
        )
    
    def get_warning_tests(self) -> List[TestPerformanceInfo]:
        """Get tests with warning performance (1s - 5s)."""
        return self.get_slow_tests(level=PerformanceLevel.WARNING)
    
    def get_average_duration(self) -> float:
        """Calculate average test duration."""
        if not self.tests:
            return 0.0
        
        total_duration = sum(test.duration for test, _ in self.tests)
        return total_duration / len(self.tests)
    
    def get_median_duration(self) -> float:
        """Calculate median test duration."""
        if not self.tests:
            return 0.0
        
        durations = sorted([test.duration for test, _ in self.tests])
        n = len(durations)
        
        if n % 2 == 0:
            return (durations[n//2 - 1] + durations[n//2]) / 2
        else:
            return durations[n//2]
    
    def get_percentile(self, p: float) -> float:
        """
        Get duration at percentile p (0-100).
        
        Args:
            p: Percentile (0-100)
            
        Returns:
            Duration at percentile
        """
        if not self.tests:
            return 0.0
        
        durations = sorted([test.duration for test, _ in self.tests])
        n = len(durations)
        k = int((p / 100) * n)
        
        return durations[min(k, n-1)]
    
    def get_performance_distribution(self) -> Dict[PerformanceLevel, int]:
        """
        Get distribution of tests across performance levels.
        
        Returns:
            Dictionary mapping level to count
        """
        distribution = {level: 0 for level in PerformanceLevel}
        
        for test, _ in self.tests:
            level = self.classify_performance(test.duration)
            distribution[level] += 1
        
        return distribution
    
    def get_performance_summary(self) -> Dict[str, any]:
        """
        Get comprehensive performance summary.
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.tests:
            return {"total_tests": 0}
        
        durations = [test.duration for test, _ in self.tests]
        distribution = self.get_performance_distribution()
        
        return {
            "total_tests": len(self.tests),
            "average_duration": self.get_average_duration(),
            "median_duration": self.get_median_duration(),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations),
            "p50": self.get_percentile(50),
            "p90": self.get_percentile(90),
            "p95": self.get_percentile(95),
            "p99": self.get_percentile(99),
            "distribution": {
                level.value: count 
                for level, count in distribution.items()
            },
            "critical_count": distribution[PerformanceLevel.CRITICAL],
            "warning_count": distribution[PerformanceLevel.WARNING],
            "slow_test_percentage": (
                (distribution[PerformanceLevel.CRITICAL] + distribution[PerformanceLevel.WARNING])
                / len(self.tests) * 100
            )
        }
    
    def flag_slow_tests(self) -> Dict[str, List[TestPerformanceInfo]]:
        """
        Flag tests by performance level.
        
        Returns:
            Dictionary mapping severity to list of tests
        """
        return {
            "critical": self.get_critical_tests(),
            "warning": self.get_warning_tests(),
            "acceptable": self.get_slow_tests(level=PerformanceLevel.ACCEPTABLE)
        }
    
    def generate_performance_report(self) -> str:
        """
        Generate human-readable performance report.
        
        Returns:
            Formatted performance report
        """
        summary = self.get_performance_summary()
        flagged = self.flag_slow_tests()
        
        report = []
        report.append("=" * 70)
        report.append("PERFORMANCE MONITORING REPORT")
        report.append("=" * 70)
        report.append(f"Language: {self.language.value}")
        report.append("")
        
        report.append("Overall Statistics:")
        report.append(f"  Total Tests: {summary['total_tests']}")
        report.append(f"  Average Duration: {summary['average_duration']:.3f}s")
        report.append(f"  Median Duration: {summary['median_duration']:.3f}s")
        report.append(f"  Min Duration: {summary['min_duration']:.3f}s")
        report.append(f"  Max Duration: {summary['max_duration']:.3f}s")
        report.append(f"  Total Duration: {summary['total_duration']:.2f}s")
        report.append("")
        
        report.append("Percentiles:")
        report.append(f"  P50 (median): {summary['p50']:.3f}s")
        report.append(f"  P90: {summary['p90']:.3f}s")
        report.append(f"  P95: {summary['p95']:.3f}s")
        report.append(f"  P99: {summary['p99']:.3f}s")
        report.append("")
        
        report.append("Performance Distribution:")
        for level, count in summary['distribution'].items():
            percentage = (count / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
            report.append(f"  {level.upper()}: {count} ({percentage:.1f}%)")
        report.append("")
        
        report.append("Slow Test Analysis:")
        report.append(f"  Critical (>5s): {summary['critical_count']} tests")
        report.append(f"  Warning (1-5s): {summary['warning_count']} tests")
        report.append(f"  Slow Test Percentage: {summary['slow_test_percentage']:.1f}%")
        report.append("")
        
        if flagged['critical']:
            report.append("⚠️  CRITICAL TESTS (>5s):")
            for info in flagged['critical'][:5]:  # Top 5
                report.append(
                    f"  - {info.test.name} ({info.suite_name}): "
                    f"{info.test.duration:.2f}s "
                    f"({info.times_slower_than_average:.1f}x avg)"
                )
            if len(flagged['critical']) > 5:
                report.append(f"  ... and {len(flagged['critical']) - 5} more")
            report.append("")
        
        if flagged['warning']:
            report.append("⚡ WARNING TESTS (1-5s):")
            for info in flagged['warning'][:5]:  # Top 5
                report.append(
                    f"  - {info.test.name} ({info.suite_name}): "
                    f"{info.test.duration:.2f}s"
                )
            if len(flagged['warning']) > 5:
                report.append(f"  ... and {len(flagged['warning']) - 5} more")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


# Utility functions

def analyze_test_performance(
    summary: ExecutionSummary,
    language: Language = Language.UNKNOWN
) -> Dict[str, any]:
    """
    Quick analysis of test performance from execution summary.
    
    Args:
        summary: Execution summary to analyze
        language: Programming language
        
    Returns:
        Performance analysis results
    """
    monitor = PerformanceMonitor(language=language)
    monitor.add_summary(summary)
    
    return {
        "summary": monitor.get_performance_summary(),
        "slow_tests": {
            "critical": len(monitor.get_critical_tests()),
            "warning": len(monitor.get_warning_tests())
        },
        "distribution": monitor.get_performance_distribution()
    }


def flag_slow_tests_simple(
    tests: List[TestResult],
    warning_threshold: float = 1.0,
    critical_threshold: float = 5.0
) -> Dict[str, List[TestResult]]:
    """
    Simple slow test flagging without full monitoring.
    
    Args:
        tests: List of test results
        warning_threshold: Warning threshold in seconds
        critical_threshold: Critical threshold in seconds
        
    Returns:
        Dictionary with categorized tests
    """
    return {
        "critical": [t for t in tests if t.duration > critical_threshold],
        "warning": [t for t in tests if warning_threshold < t.duration <= critical_threshold],
        "fast": [t for t in tests if t.duration <= warning_threshold]
    }

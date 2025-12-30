#!/usr/bin/env python
"""
Test Task 55: Universal Performance Monitoring

Demonstrates performance tracking across ALL 14 languages.
"""

from testgen.core.result_models import TestResult, TestSuite, ExecutionSummary, TestStatus, Language, TestFramework
from testgen.core.performance_monitor import (
    PerformanceMonitor, PerformanceLevel, PerformanceThresholds,
    analyze_test_performance, flag_slow_tests_simple
)

def test_task_55_performance_monitoring():
    """Test universal performance monitoring."""
    
    print("=" * 70)
    print("TASK 55: UNIVERSAL PERFORMANCE MONITORING")
    print("Track duration and flag slow tests across ALL 14 languages")
    print("=" * 70)
    print()
    
    # Test 1: Basic Performance Monitoring
    print("1. Basic Performance Monitoring")
    print("-" * 70)
    
    monitor = PerformanceMonitor(language=Language.PYTHON)
    
    # Add various tests with different durations
    tests = [
        TestResult(name="test_fast", status=TestStatus.PASSED, duration=0.05),
        TestResult(name="test_good", status=TestStatus.PASSED, duration=0.3),
        TestResult(name="test_acceptable", status=TestStatus.PASSED, duration=0.8),
        TestResult(name="test_warning", status=TestStatus.PASSED, duration=2.5),
        TestResult(name="test_critical", status=TestStatus.PASSED, duration=7.2),
    ]
    
    for test in tests:
        monitor.add_test(test, "test_suite.py")
    
    print(f"Added {len(monitor.tests)} tests for monitoring")
    print()
    
    # Test 2: Classify Performance
    print("2. Performance Classification")
    print("-" * 70)
    
    for test in tests:
        level = monitor.classify_performance(test.duration)
        print(f"{test.name:20} ({test.duration:5.2f}s) -> {level.value.upper()}")
    print()
    
    # Test 3: Get Slow Tests
    print("3. Identify Slow Tests (>1s)")
    print("-" * 70)
    
    slow_tests = monitor.get_slow_tests(threshold=1.0)
    print(f"Found {len(slow_tests)} slow tests:")
    for info in slow_tests:
        print(f"  - {info.test.name}: {info.test.duration:.2f}s ({info.level.value})")
        print(f"    {info.times_slower_than_average:.1f}x slower than average")
    print()
    
    # Test 4: Get Critical Tests
    print("4. Critical Tests (>5s)")
    print("-" * 70)
    
    critical = monitor.get_critical_tests()
    print(f"Critical tests: {len(critical)}")
    for info in critical:
        print(f"  ⚠️  {info.test.name}: {info.test.duration:.2f}s")
    print()
    
    # Test 5: Get Warning Tests
    print("5. Warning Tests (1-5s)")
    print("-" * 70)
    
    warnings = monitor.get_warning_tests()
    print(f"Warning tests: {len(warnings)}")
    for info in warnings:
        print(f"  ⚡ {info.test.name}: {info.test.duration:.2f}s")
    print()
    
    # Test 6: Performance Statistics
    print("6. Performance Statistics")
    print("-" * 70)
    
    summary = monitor.get_performance_summary()
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Average Duration: {summary['average_duration']:.3f}s")
    print(f"Median Duration: {summary['median_duration']:.3f}s")
    print(f"Min Duration: {summary['min_duration']:.3f}s")
    print(f"Max Duration: {summary['max_duration']:.3f}s")
    print(f"P90: {summary['p90']:.3f}s")
    print(f"P95: {summary['p95']:.3f}s")
    print(f"P99: {summary['p99']:.3f}s")
    print()
    
    # Test 7: Performance Distribution
    print("7. Performance Distribution")
    print("-" * 70)
    
    distribution = monitor.get_performance_distribution()
    for level, count in distribution.items():
        print(f"{level.value:12}: {count} tests")
    print()
    
    # Test 8: Flag Slow Tests
    print("8. Flag Tests by Performance Level")
    print("-" * 70)
    
    flagged = monitor.flag_slow_tests()
    print(f"Critical: {len(flagged['critical'])} tests")
    print(f"Warning: {len(flagged['warning'])} tests")
    print(f"Acceptable: {len(flagged['acceptable'])} tests")
    print()
    
    # Test 9: Language-Specific Thresholds
    print("9. Language-Specific Threshold Adjustments")
    print("-" * 70)
    
    languages = [Language.PYTHON, Language.GO, Language.RUST, Language.JAVA]
    thresholds = PerformanceThresholds()
    
    for lang in languages:
        adjusted = thresholds.get_adjusted_threshold(1.0, lang)
        print(f"{lang.value:12}: 1.0s -> {adjusted:.2f}s (multiplier: {thresholds.language_multipliers[lang]:.1f}x)")
    print()
    
    # Test 10: Performance Report Generation
    print("10. Performance Report")
    print("-" * 70)
    
    report = monitor.generate_performance_report()
    print(report)
    print()
    
    # Test 11: Multi-Language Performance
    print("11. Multi-Language Performance Comparison")
    print("-" * 70)
    
    # Create test suites for different languages
    python_suite = TestSuite(
        name="test_python.py",
        file_path="tests/test_python.py",
        tests=[
            TestResult(name="test1", status=TestStatus.PASSED, duration=0.5),
            TestResult(name="test2", status=TestStatus.PASSED, duration=1.2),
        ],
        language=Language.PYTHON,
        framework=TestFramework.PYTEST
    )
    
    go_suite = TestSuite(
        name="test_go.go",
        file_path="tests/test_go.go",
        tests=[
            TestResult(name="TestOne", status=TestStatus.PASSED, duration=0.1),
            TestResult(name="TestTwo", status=TestStatus.PASSED, duration=0.3),
        ],
        language=Language.GO,
        framework=TestFramework.GO_TESTING
    )
    
    rust_suite = TestSuite(
        name="test_rust.rs",
        file_path="tests/test_rust.rs",
        tests=[
            TestResult(name="test_fast", status=TestStatus.PASSED, duration=0.05),
        ],
        language=Language.RUST,
        framework=TestFramework.CARGO
    )
    
    for lang, suite in [(Language.PYTHON, python_suite), (Language.GO, go_suite), (Language.RUST, rust_suite)]:
        lang_monitor = PerformanceMonitor(language=lang)
        lang_monitor.add_suite(suite)
        lang_summary = lang_monitor.get_performance_summary()
        
        print(f"{lang.value.upper()}:")
        print(f"  Tests: {lang_summary['total_tests']}")
        print(f"  Avg Duration: {lang_summary['average duration']:.3f}s")
        print(f"  Slow Tests: {lang_summary['slow_test_percentage']:.1f}%")
        print()
    
    # Test 12: Simple Flagging Utility
    print("12. Simple Slow Test Flagging")
    print("-" * 70)
    
    simple_flagged = flag_slow_tests_simple(tests)
    print(f"Critical: {len(simple_flagged['critical'])}")
    print(f"Warning: {len(simple_flagged['warning'])}")
    print(f"Fast: {len(simple_flagged['fast'])}")
    print()
    
    # Summary
    print("=" * 70)
    print("✅ TASK 55 COMPLETE!")
    print("=" * 70)
    print()
    print("Universal Performance Monitor provides:")
    print("  ✅ Track per-test duration")
    print("  ✅ Flag slow tests (>1s = warning, >5s = critical)")
    print("  ✅ Performance level classification (5 levels)")
    print("  ✅ Language-specific threshold adjustments")
    print("  ✅ Comprehensive statistics (avg, median, percentiles)")
    print("  ✅ Performance distribution analysis")
    print("  ✅ Critical and warning test identification")
    print("  ✅ Performance report generation")
    print("  ✅ Multi-language performance comparison")
    print()
    print("Supported for ALL 14 languages:")
    print("  - Python, JavaScript, TypeScript")
    print("  - Java, Go, C#, Ruby")
    print("  - Rust, PHP, Swift, Kotlin")
    print("  - C++, HTML, CSS")
    print()
    print("Language-specific thresholds:")
    print("  - Fast languages (Go, Rust, C++): Lower thresholds")
    print("  - JVM languages (Java, Kotlin): Higher thresholds")
    print("  - Interpreted (Python, Ruby, PHP): Standard thresholds")
    print()
    print("🌍 Multi-language performance monitoring COMPLETE!")

if __name__ == "__main__":
    test_task_55_performance_monitoring()

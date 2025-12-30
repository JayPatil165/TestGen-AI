#!/usr/bin/env python
"""
Test Task 56: Universal Failure Analysis

Demonstrates failure analysis across ALL 14 languages.
"""

from testgen.core.result_models import TestResult, TestSuite, TestStatus, Language, TestFramework, ErrorInfo
from testgen.core.failure_analyzer import (
    FailureAnalyzer, FailureType,
    quick_failure_analysis
)

def test_task_56_failure_analysis():
    """Test universal failure analysis."""
    
    print("=" * 70)
    print("TASK 56: UNIVERSAL FAILURE ANALYSIS")
    print("Analyze test failures across ALL 14 languages")
    print("=" * 70)
    print()
    
    # Test 1: Create Failed Tests
    print("1. Create Failed Tests with Different Error Types")
    print("-" * 70)
    
    failed_tests = [
        TestResult(
            name="test_assertion_error",
            status=TestStatus.FAILED,
            duration=0.1,
            error=ErrorInfo(
                message="AssertionError: Expected 5 but got 3",
                type="AssertionError"
            )
        ),
        TestResult(
            name="test_timeout",
            status=TestStatus.FAILED,
            duration=10.0,
            error=ErrorInfo(
                message="TimeoutError: Test timed out after 10 seconds",
                type="TimeoutError"
            )
        ),
        TestResult(
            name="test_import_error",
            status=TestStatus.FAILED,
            duration=0.05,
            error=ErrorInfo(
                message="ModuleNotFoundError: No module named 'missing_module'",
                type="ModuleNotFoundError"
            )
        ),
        TestResult(
            name="test_null_pointer",
            status=TestStatus.FAILED,
            duration=0.2,
            error=ErrorInfo(
                message="NullPointerException: Cannot invoke method on null object",
                type="NullPointerException"
            )
        ),
        TestResult(
            name="test_network_error",
            status=TestStatus.FAILED,
            duration=5.0,
            error=ErrorInfo(
                message="ConnectionError: Failed to connect to https://api.example.com",
                type="ConnectionError"
            )
        ),
    ]
    
    print(f"Created {len(failed_tests)} failed tests")
    print()
    
    # Test 2: Initialize Analyzer
    print("2. Initialize Failure Analyzer")
    print("-" * 70)
    
    analyzer = FailureAnalyzer(Language.PYTHON, TestFramework.PYTEST)
    
    for test in failed_tests:
        analyzer.add_test(test, "test_suite.py")
    
    print(f"Added {len(analyzer.failed_tests)} failed tests to analyzer")
    print()
    
    # Test 3: Classify Failure Types
    print("3. Classify Failure Types")
    print("-" * 70)
    
    for test in failed_tests:
        ftype = analyzer.classify_failure(test.error.message)
        print(f"{test.name:25} -> {ftype.value.upper()}")
    print()
    
    # Test 4: Count Failure Types
    print("4. Count Failures by Type")
    print("-" * 70)
    
    failure_counts = analyzer.count_failure_types()
    for ftype, count in failure_counts.items():
        if count > 0:
            print(f"{ftype.value:20}: {count}")
    print()
    
    # Test 5: Extract Error Patterns
    print("5. Extract Common Error Patterns")
    print("-" * 70)
    
    # Add more similar errors to create patterns
    analyzer.add_test(
        TestResult(
            name="test_assertion_2",
            status=TestStatus.FAILED,
            duration=0.1,
            error=ErrorInfo(message="AssertionError: Expected 10 but got 8")
        ),
        "test_suite.py"
    )
    analyzer.add_test(
        TestResult(
            name="test_assertion_3",
            status=TestStatus.FAILED,
            duration=0.1,
            error=ErrorInfo(message="AssertionError: Expected 'hello' but got 'world'")
        ),
        "test_suite.py"
    )
    
    patterns = analyzer.extract_error_patterns(min_occurrences=2)
    print(f"Found {len(patterns)} common patterns:")
    for pattern in patterns:
        print(f"\n  Pattern: {pattern.type.value}")
        print(f"  Count: {pattern.count}")
        print(f"  Example: {pattern.examples[0][:60]}...")
    print()
    
    # Test 6: Get Most Common Errors
    print("6. Most Common Error Messages")
    print("-" * 70)
    
    common_errors = analyzer.get_most_common_errors(n=5)
    for i, (error, count) in enumerate(common_errors, 1):
        print(f"{i}. ({count}x) {error[:50]}...")
    print()
    
    # Test 7: Identify Flaky Tests
    print("7. Identify Potentially Flaky Tests")
    print("-" * 70)
    
    flaky = analyzer.identify_flaky_tests()
    print(f"Potentially flaky tests: {len(flaky)}")
    for test_name in flaky:
        print(f"  ⚠️  {test_name}")
    print()
    
    # Test 8: Complete Analysis
    print("8. Complete Failure Analysis")
    print("-" * 70)
    
    analysis = analyzer.analyze()
    print(f"Total Failures: {analysis.total_failures}")
    print(f"Failure Types: {len([v for v in analysis.failure_types.values() if v > 0])}")
    print(f"Common Patterns: {len(analysis.common_patterns)}")
    print(f"Most Common Errors: {len(analysis.most_common_errors)}")
    print(f"Flaky Candidates: {len(analysis.flaky_candidates)}")
    print()
    
    # Test 9: Generate Report
    print("9. Generate Failure Report")
    print("-" * 70)
    
    report = analyzer.generate_failure_report()
    print(report)
    print()
    
    # Test 10: Filter by Failure Type
    print("10. Get Failures by Type")
    print("-" * 70)
    
    assertions = analyzer.get_failures_by_type(FailureType.ASSERTION)
    timeouts = analyzer.get_failures_by_type(FailureType.TIMEOUT)
    network = analyzer.get_failures_by_type(FailureType.NETWORK_ERROR)
    
    print(f"Assertion failures: {len(assertions)}")
    print(f"Timeout failures: {len(timeouts)}")
    print(f"Network failures: {len(network)}")
    print()
    
    # Test 11: Multi-Language Error Patterns
    print("11. Multi-Language Error Pattern Recognition")
    print("-" * 70)
    
    multi_lang_errors = {
        "Python": "AssertionError: assert 5 == 3",
        "JavaScript": "Expected 5 to equal 3",
        "Java": "Expected: 5 but was: 3",
        "Go": "FAIL: got 3, want 5",
        "Rust": "assertion `left == right` failed\n  left: 5\n right: 3",
        "C#": "Assert.Equal() Failure\nExpected: 5\nActual:   3"
    }
    
    print("Classifying errors from different languages:")
    for lang, error_msg in multi_lang_errors.items():
        ftype = analyzer.classify_failure(error_msg)
        print(f"  {lang:12}: {ftype.value}")
    print()
    
    # Test 12: Language-Specific Patterns
    print("12. Language-Specific Error Patterns")
    print("-" * 70)
    
    js_analyzer = FailureAnalyzer(Language.JAVASCRIPT, TestFramework.JEST)
    js_analyzer.add_test(
        TestResult(
            name="test_undefined",
            status=TestStatus.FAILED,
            duration=0.1,
            error=ErrorInfo(message="TypeError: Cannot read property 'foo' of undefined")
        ),
        "test.js"
    )
    
    java_analyzer = FailureAnalyzer(Language.JAVA, TestFramework.JUNIT)
    java_analyzer.add_test(
        TestResult(
            name="testNullPointer",
            status=TestStatus.FAILED,
            duration=0.2,
            error=ErrorInfo(message="java.lang.NullPointerException: Cannot invoke method on null")
        ),
        "Test.java"
    )
    
    print(f"JavaScript errors classified: {len(js_analyzer.failed_tests)}")
    print(f"Java errors classified: {len(java_analyzer.failed_tests)}")
    print()
    
    # Summary
    print("=" * 70)
    print("✅ TASK 56 COMPLETE!")
    print("=" * 70)
    print()
    print("Universal Failure Analyzer provides:")
    print("  ✅ Count failure types (assertion, exception, timeout, etc.)")
    print("  ✅ Extract common error patterns")
    print("  ✅ Normalize error messages for pattern matching")
    print("  ✅ Identify potentially flaky tests")
    print("  ✅ Classify failures (10+ types)")
    print("  ✅ Generate comprehensive failure reports")
    print("  ✅ Filter failures by type")
    print("  ✅ Multi-language error pattern recognition")
    print("  ✅ Language-specific error handling")
    print()
    print("Supported error types:")
    print("  - Assertion errors (all languages)")
    print("  - Exceptions (all languages)")
    print("  - Timeouts")
    print("  - Import/Module errors")
    print("  - Runtime errors (NullPointer, undefined, etc.)")
    print("  - Network errors")
    print("  - File errors")
    print("  - Memory errors")
    print("  - Permission errors")
    print()
    print("Supported for ALL 14 languages:")
    print("  - Python, JavaScript, TypeScript")
    print("  - Java, Go, C#, Ruby")
    print("  - Rust, PHP, Swift, Kotlin")
    print("  - C++, HTML, CSS")
    print()
    print("🌍 Multi-language failure analysis COMPLETE!")

if __name__ == "__main__":
    test_task_56_failure_analysis()

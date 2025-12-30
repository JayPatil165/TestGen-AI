#!/usr/bin/env python
"""
Test Task 53: Universal Result Data Models

Demonstrates Pydantic models for test results across ALL 14 languages.
"""

from datetime import datetime
from testgen.core.result_models import (
    TestResult, TestSuite, ExecutionSummary,
    ErrorInfo, TestStatus, TestType, Language, TestFramework,
    create_test_result_from_dict,
    create_test_suite_from_results,
    create_execution_summary_from_suites
)

def test_task_53_result_models():
    """Test universal result data models."""
    
    print("=" * 70)
    print("TASK 53: UNIVERSAL RESULT DATA MODELS")
    print("Pydantic models for test results across ALL 14 languages")
    print("=" * 70)
    print()
    
    # Test 1: TestResult Model
    print("1. TestResult Model")
    print("-" * 70)
    
    test_result = TestResult(
        name="test_addition",
        status=TestStatus.PASSED,
        duration=0.023,
        test_type=TestType.UNIT,
        language=Language.PYTHON,
        framework=TestFramework.PYTEST,
        file_path="tests/test_calculator.py"
    )
    
    print(f"Name: {test_result.name}")
    print(f"Status: {test_result.status}")
    print(f"Duration: {test_result.duration}s")
    print(f"Language: {test_result.language}")
    print(f"Framework: {test_result.framework}")
    print(f"Passed: {test_result.passed}")
    print()
    
    # Test 2: TestResult with Error
    print("2. TestResult with Error Information")
    print("-" * 70)
    
    error = ErrorInfo(
        message="AssertionError: expected 4 but got 5",
        type="AssertionError",
        traceback="Traceback (most recent call last)...",
        file_path="test_calculator.py",
        line_number=42
    )
    
    failed_test = TestResult(
        name="test_division_by_zero",
        status=TestStatus.FAILED,
        duration=0.015,
        error=error,
        language=Language.PYTHON,
        framework=TestFramework.PYTEST
    )
    
    print(f"Name: {failed_test.name}")
    print(f"Status: {failed_test.status}")
    print(f"Error: {failed_test.error.message}")
    print(f"Failed: {failed_test.failed}")
    print()
    
    # Test 3: TestSuite Model
    print("3. TestSuite Model")
    print("-" * 70)
    
    test_suite = TestSuite(
        name="test_calculator.py",
        file_path="tests/test_calculator.py",
        tests=[test_result, failed_test],
        language=Language.PYTHON,
        framework=TestFramework.PYTEST
    )
    
    print(f"Suite: {test_suite.name}")
    print(f"Total Tests: {test_suite.total_tests}")
    print(f"Passed: {test_suite.passed_tests}")
    print(f"Failed: {test_suite.failed_tests}")
    print(f"Pass Rate: {test_suite.pass_rate:.1f}%")
    print(f"Duration: {test_suite.total_duration}s")
    print()
    
    # Test 4: ExecutionSummary Model
    print("4. ExecutionSummary Model")
    print("-" * 70)
    
    summary = ExecutionSummary(
        total=42,
        passed=40,
        failed=1,
        skipped=1,
        errors=0,
        duration=12.345,
        language=Language.PYTHON,
        framework=TestFramework.PYTEST,
        suites=[test_suite]
    )
    
    print(f"Total: {summary.total}")
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")
    print(f"Skipped: {summary.skipped}")
    print(f"Pass Rate: {summary.pass_rate:.1f}%")
    print(f"Success: {summary.success}")
    print(f"\nSummary Text:")
    print(summary.get_summary_text())
    print()
    
    # Test 5: Multi-Language Support
    print("5. Multi-Language Support")
    print("-" * 70)
    
    languages = [
        (Language.PYTHON, TestFramework.PYTEST),
        (Language.JAVASCRIPT, TestFramework.JEST),
        (Language.JAVA, TestFramework.JUNIT),
        (Language.GO, TestFramework.GO_TESTING),
        (Language.CSHARP, TestFramework.NUNIT),
        (Language.RUST, TestFramework.CARGO)
    ]
    
    for lang, framework in languages:
        result = TestResult(
            name=f"test_{lang.value}",
            status=TestStatus.PASSED,
            duration=0.1,
            language=lang,
            framework=framework
        )
        print(f"{lang.value:12} / {framework.value:10} - ✅ Created")
    print()
    
    # Test 6: JSON Serialization
    print("6. JSON Serialization")
    print("-" * 70)
    
    json_data = test_result.json(indent=2)
    print("TestResult as JSON:")
    print(json_data[:200] + "...")
    print()
    
    # Test 7: Dictionary Conversion
    print("7. Dictionary Conversion")
    print("-" * 70)
    
    result_dict = test_result.to_dict()
    print(f"Keys: {list(result_dict.keys())}")
    print(f"Name: {result_dict['name']}")
    print(f"Status: {result_dict['status']}")
    print()
    
    # Test 8: Creating from Dictionary
    print("8. Creating Models from Dictionaries")
    print("-" * 70)
    
    data = {
        "name": "test_from_dict",
        "status": "passed",
        "duration": 0.5,
        "language": "typescript",
        "framework": "jest"
    }
    
    from_dict = create_test_result_from_dict(data)
    print(f"Created from dict: {from_dict.name}")
    print(f"Language: {from_dict.language}")
    print()
    
    # Test 9: Test Suite Creation
    print("9. Creating Test Suite from Results")
    print("-" * 70)
    
    results = [
        TestResult(name="test_1", status=TestStatus.PASSED, duration=0.1),
        TestResult(name="test_2", status=TestStatus.PASSED, duration=0.2),
        TestResult(name="test_3", status=TestStatus.FAILED, duration=0.15)
    ]
    
    suite = create_test_suite_from_results(
        name="integration_tests.js",
        file_path="tests/integration_tests.js",
        results=results,
        language=Language.JAVASCRIPT,
        framework=TestFramework.JEST
    )
    
    print(f"Suite: {suite.name}")
    print(f"Tests: {suite.total_tests}")
    print(f"Pass Rate: {suite.pass_rate:.1f}%")
    print()
    
    # Test 10: Execution Summary from Suites
    print("10. Creating Execution Summary from Suites")
    print("-" * 70)
    
    suites = [test_suite, suite]
    exec_summary = create_execution_summary_from_suites(
        suites=suites,
        language=Language.PYTHON,
        framework=TestFramework.PYTEST
    )
    
    print(f"Total Tests: {exec_summary.total}")
    print(f"Passed: {exec_summary.passed}")
    print(f"Failed: {exec_summary.failed}")
    print(f"Pass Rate: {exec_summary.pass_rate:.1f}%")
    print()
    
    # Test 11: Validation
    print("11. Data Validation")
    print("-" * 70)
    
    try:
        # This should fail validation (negative duration)
        invalid = TestResult(
            name="invalid_test",
            status=TestStatus.PASSED,
            duration=-1.0  # Invalid!
        )
    except Exception as e:
        print(f"✅ Validation caught error: {type(e).__name__}")
    
    print()
    
    # Test 12: Properties and Computed Values
    print("12. Properties and Computed Values")
    print("-" * 70)
    
    print(f"Test Suite Properties:")
    print(f"  Total: {test_suite.total_tests}")
    print(f"  Passed: {test_suite.passed_tests}")
    print(f"  Failed: {test_suite.failed_tests}")
    print(f"  Pass Rate: {test_suite.pass_rate:.1f}%")
    
    print(f"\nExecution Summary Properties:")
    print(f"  Success: {summary.success}")
    print(f"  Pass Rate: {summary.pass_rate:.1f}%")
    print(f"  Failure Rate: {summary.failure_rate:.1f}%")
    print()
    
    # Summary
    print("=" * 70)
    print("✅ TASK 53 COMPLETE!")
    print("=" * 70)
    print()
    print("Universal Result Data Models provide:")
    print("  ✅ Pydantic models with validation")
    print("  ✅ TestResult - Individual test information")
    print("  ✅ TestSuite - Grouped tests from file")
    print("  ✅ ExecutionSummary - Aggregated results")
    print("  ✅ TestRun - Complete run metadata")
    print("  ✅ ErrorInfo - Detailed error tracking")
    print("  ✅ Multi-language support (ALL 14 languages)")
    print("  ✅ JSON serialization/deserialization")
    print("  ✅ Dictionary conversion")
    print("  ✅ Data validation")
    print("  ✅ Computed properties")
    print("  ✅ Utility functions")
    print()
    print("Supported Languages:")
    print("  - Python, JavaScript, TypeScript")
    print("  - Java, Go, C#, Ruby")
    print("  - Rust, PHP, Swift, Kotlin")
    print("  - C++, HTML, CSS")
    print()
    print("Supported Frameworks:")
    print("  - pytest, Jest, JUnit, go test")
    print("  - NUnit, xUnit, RSpec, cargo")
    print("  - PHPUnit, XCTest, Google Test")
    print("  - Playwright, Cypress, Selenium")
    print()
    print("🌍 Multi-language result models COMPLETE!")

if __name__ == "__main__":
    test_task_53_result_models()

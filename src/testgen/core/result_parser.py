"""
Universal Test Result Parser for TestGen AI.

Parses test output from ANY test framework across 14 languages.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TestFailure:
    """Detailed information about a test failure."""
    message: str
    traceback: Optional[str] = None
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    exception_type: Optional[str] = None


@dataclass
class IndividualTestResult:
    """
    Detailed result for a single test.
    
    Works across all 14 languages with consistent format.
    """
    name: str
    status: str  # passed, failed, skipped, error
    duration: float = 0.0
    failure: Optional[TestFailure] = None
    language: str = "unknown"
    framework: str = "unknown"
    
    @property
    def passed(self) -> bool:
        return self.status == "passed"
    
    @property
    def failed(self) -> bool:
        return self.status == "failed"
    
    @property
    def skipped(self) -> bool:
        return self.status == "skipped"


@dataclass
class ParsedTestResults:
    """
    Complete parsed test results for any language.
    
    Aggregates individual test results with summary statistics.
    """
    tests: List[IndividualTestResult] = field(default_factory=list)
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    language: str = "unknown"
    framework: str = "unknown"
    raw_output: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def success(self) -> bool:
        return self.failed == 0 and self.errors == 0
    
    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    def get_failed_tests(self) -> List[IndividualTestResult]:
        """Get all failed tests."""
        return [t for t in self.tests if t.failed]
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        status = "✅ PASSED" if self.success else "❌ FAILED"
        return (
            f"{status} - {self.language}/{self.framework}\n"
            f"  Total: {self.total}, Passed: {self.passed}, "
            f"Failed: {self.failed}, Skipped: {self.skipped}\n"
            f"  Duration: {self.duration:.2f}s, Pass Rate: {self.pass_rate:.1f}%"
        )


class UniversalTestResultParser:
    """
    Universal parser for test results from ANY framework.
    
    Handles all 14 languages with framework-specific parsing.
    """
    
    def __init__(self, language: str, framework: str):
        """
        Initialize parser for specific language/framework.
        
        Args:
            language: Programming language
            framework: Test framework
        """
        self.language = language.lower()
        self.framework = framework.lower()
    
    def parse(
        self,
        output: str,
        json_file: Optional[str] = None
    ) -> ParsedTestResults:
        """
        Parse test output into structured results.
        
        Args:
            output: Raw test output (stdout)
            json_file: Optional JSON report file
            
        Returns:
            ParsedTestResults with detailed information
        """
        results = ParsedTestResults(
            language=self.language,
            framework=self.framework,
            raw_output=output
        )
        
        # Try JSON parsing first if file provided
        if json_file and Path(json_file).exists():
            json_results = self._parse_json_report(json_file)
            if json_results:
                return json_results
        
        # Fall back to text parsing based on framework
        if self.framework == "pytest":
            return self._parse_pytest(output)
        elif self.framework == "jest":
            return self._parse_jest(output)
        elif self.framework == "junit":
            return self._parse_junit(output)
        elif self.framework == "testing":  # Go
            return self._parse_go(output)
        elif self.framework == "nunit":
            return self._parse_nunit(output)
        elif self.framework == "rspec":
            return self._parse_rspec(output)
        elif self.framework == "cargo":  # Rust
            return self._parse_cargo(output)
        elif self.framework == "phpunit":
            return self._parse_phpunit(output)
        elif self.framework == "xctest":  # Swift
            return self._parse_xctest(output)
        elif self.framework == "gtest":  # C++
            return self._parse_gtest(output)
        elif self.framework == "playwright":
            return self._parse_playwright(output)
        else:
            # Generic parsing for unknown frameworks
            return self._parse_generic(output, results)
    
    def _parse_json_report(self, json_file: str) -> Optional[ParsedTestResults]:
        """Parse JSON test report (pytest-json-report, Jest JSON, etc.)."""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Detect JSON format and parse accordingly
            if "summary" in data and "tests" in data:
                # pytest-json-report format
                return self._parse_pytest_json(data)
            elif "numTotalTests" in data:
                # Jest JSON format
                return self._parse_jest_json(data)
            else:
                return None
        except Exception:
            return None
    
    def _parse_pytest_json(self, data: Dict) -> ParsedTestResults:
        """Parse pytest JSON report."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        summary = data.get("summary", {})
        results.total = summary.get("total", 0)
        results.passed = summary.get("passed", 0)
        results.failed = summary.get("failed", 0)
        results.skipped = summary.get("skipped", 0)
        results.errors = summary.get("error", 0)
        results.duration = data.get("duration", 0.0)
        
        # Parse individual tests
        for test in data.get("tests", []):
            failure = None
            if test.get("outcome") == "failed":
                call_info = test.get("call", {})
                failure = TestFailure(
                    message=call_info.get("longrepr", ""),
                    traceback=call_info.get("crash", {}).get("traceback"),
                    line_number=call_info.get("lineno")
                )
            
            results.tests.append(IndividualTestResult(
                name=test.get("nodeid", "unknown"),
                status=test.get("outcome", "unknown"),
                duration=test.get("duration", 0.0),
                failure=failure,
                language=self.language,
                framework=self.framework
            ))
        
        return results
    
    def _parse_jest_json(self, data: Dict) -> ParsedTestResults:
        """Parse Jest JSON output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        results.total = data.get("numTotalTests", 0)
        results.passed = data.get("numPassedTests", 0)
        results.failed = data.get("numFailedTests", 0)
        results.skipped = data.get("numPendingTests", 0)
        
        # Parse individual tests
        for test_file in data.get("testResults", []):
            for assertion in test_file.get("assertionResults", []):
                failure = None
                if assertion.get("status") == "failed":
                    failure_msgs = assertion.get("failureMessages", [])
                    failure = TestFailure(
                        message=failure_msgs[0] if failure_msgs else ""
                    )
                
                results.tests.append(IndividualTestResult(
                    name=assertion.get("fullName", "unknown"),
                    status=assertion.get("status", "unknown"),
                    duration=assertion.get("duration", 0) / 1000.0,  # Convert ms to s
                    failure=failure,
                    language=self.language,
                    framework=self.framework
                ))
        
        return results
    
    def _parse_pytest(self, output: str) -> ParsedTestResults:
        """Parse pytest text output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        # Extract summary line
        for line in output.split('\n'):
            if 'passed' in line or 'failed' in line:
                # Example: "5 passed, 2 failed, 1 skipped in 2.5s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        try:
                            results.passed = int(parts[i-1])
                        except:
                            pass
                    elif part == 'failed' and i > 0:
                        try:
                            results.failed = int(parts[i-1])
                        except:
                            pass
                    elif part == 'skipped' and i > 0:
                        try:
                            results.skipped = int(parts[i-1])
                        except:
                            pass
                    elif 'in' in part and i > 0:
                        # Duration: "in 2.5s"
                        try:
                            duration_str = parts[i+1].rstrip('s')
                            results.duration = float(duration_str)
                        except:
                            pass
        
        results.total = results.passed + results.failed + results.skipped
        return results
    
    def _parse_jest(self, output: str) -> ParsedTestResults:
        """Parse Jest text output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if 'Tests:' in line:
                # Example: "Tests:       2 passed, 2 total"
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'passed' in part and i > 0:
                        try:
                            results.passed = int(parts[i-1])
                        except:
                            pass
                    elif 'failed' in part and i > 0:
                        try:
                            results.failed = int(parts[i-1])
                        except:
                            pass
                    elif 'total' in part and i > 0:
                        try:
                            results.total = int(parts[i-1])
                        except:
                            pass
        
        return results
    
    def _parse_junit(self, output: str) -> ParsedTestResults:
        """Parse JUnit/Gradle/Maven output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if 'Tests run:' in line:
                # Example: "Tests run: 5, Failures: 0, Errors: 0, Skipped: 1"
                parts = line.split(',')
                for part in parts:
                    if 'Tests run:' in part:
                        try:
                            results.total = int(part.split(':')[1].strip())
                        except:
                            pass
                    elif 'Failures:' in part:
                        try:
                            results.failed = int(part.split(':')[1].strip())
                        except:
                            pass
                    elif 'Errors:' in part:
                        try:
                            results.errors = int(part.split(':')[1].strip())
                        except:
                            pass
                    elif 'Skipped:' in part:
                        try:
                            results.skipped = int(part.split(':')[1].strip())
                        except:
                            pass
        
        results.passed = results.total - results.failed - results.errors - results.skipped
        return results
    
    def _parse_go(self, output: str) -> ParsedTestResults:
        """Parse Go test output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if line.startswith('PASS'):
                results.passed += 1
            elif line.startswith('FAIL'):
                results.failed += 1
            elif line.startswith('SKIP'):
                results.skipped += 1
        
        results.total = results.passed + results.failed + results.skipped
        return results
    
    def _parse_nunit(self, output: str) -> ParsedTestResults:
        """Parse NUnit/dotnet test output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if 'Passed!' in line or 'Total:' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'Passed' in part and i > 0 and parts[i-1].isdigit():
                        results.passed = int(parts[i-1])
                    elif 'Failed' in part and i > 0 and parts[i-1].isdigit():
                        results.failed = int(parts[i-1])
                    elif 'Total' in part and i > 0 and parts[i-1].isdigit():
                        results.total = int(parts[i-1])
        
        return results
    
    def _parse_rspec(self, output: str) -> ParsedTestResults:
        """Parse RSpec output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if 'examples,' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'examples' in part and i > 0:
                        try:
                            results.total = int(parts[i-1])
                        except:
                            pass
                    elif 'failures' in part and i > 0:
                        try:
                            results.failed = int(parts[i-1])
                        except:
                            pass
        
        results.passed = results.total - results.failed
        return results
    
    def _parse_cargo(self, output: str) -> ParsedTestResults:
        """Parse Rust cargo test output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if 'test result:' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'passed' in part and i > 0:
                        try:
                            results.passed = int(parts[i-1])
                        except:
                            pass
                    elif 'failed' in part and i > 0:
                        try:
                            results.failed = int(parts[i-1])
                        except:
                            pass
        
        results.total = results.passed + results.failed
        return results
    
    def _parse_phpunit(self, output: str) -> ParsedTestResults:
        """Parse PHPUnit output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if 'Tests:' in line:
                parts = line.split(',')
                for part in parts:
                    if 'Tests:' in part:
                        try:
                            results.total = int(part.split(':')[1].strip())
                        except:
                            pass
                    elif 'Failures:' in part:
                        try:
                            results.failed = int(part.split(':')[1].strip())
                        except:
                            pass
        
        results.passed = results.total - results.failed
        return results
    
    def _parse_xctest(self, output: str) -> ParsedTestResults:
        """Parse XCTest/Swift test output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if 'Test Suite' in line and 'passed' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'passed' in part.lower() and i > 0:
                        try:
                            results.passed = int(parts[i-1])
                        except:
                            pass
                    elif 'failed' in part.lower() and i > 0:
                        try:
                            results.failed = int(parts[i-1])
                        except:
                            pass
        
        results.total = results.passed + results.failed
        return results
    
    def _parse_gtest(self, output: str) -> ParsedTestResults:
        """Parse Google Test (C++) output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if '[  PASSED  ]' in line:
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        results.passed = int(part)
                        break
            elif '[  FAILED  ]' in line:
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        results.failed = int(part)
                        break
        
        results.total = results.passed + results.failed
        return results
    
    def _parse_playwright(self, output: str) -> ParsedTestResults:
        """Parse Playwright output."""
        results = ParsedTestResults(language=self.language, framework=self.framework)
        
        for line in output.split('\n'):
            if 'passed' in line.lower():
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        results.passed = int(part)
                        results.total = results.passed
                        break
        
        return results
    
    def _parse_generic(self, output: str, results: ParsedTestResults) -> ParsedTestResults:
        """Generic parser for unknown frameworks."""
        # Simple heuristic: count "PASS" and "FAIL" in output
        results.passed = output.lower().count("pass")
        results.failed = output.lower().count("fail")
        results.total = results.passed + results.failed
        return results

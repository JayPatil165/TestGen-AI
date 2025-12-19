"""
Python Test Runner (pytest-based).

Implements BaseTestRunner for Python projects using pytest.
"""

import subprocess
import json
import ast
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base_runner import BaseTestRunner, TestResults, TestResult


class PythonTestRunner(BaseTestRunner):
    """
    Test runner for Python projects using pytest.
    
    Inherits from BaseTestRunner and implements Python/pytest-specific logic.
    """
    
    def __init__(self, verbose: bool = False, capture_output: bool = True):
        """
        Initialize Python test runner.
        
        Args:
            verbose: Print verbose output
            capture_output: Capture test output
        """
        super().__init__(verbose)
        self.capture_output = capture_output
    
    def get_language(self) -> str:
        """Get language name."""
        return "python"
    
    def get_framework(self) -> str:
        """Get test framework name."""
        return "pytest"
    
    def get_test_patterns(self) -> List[str]:
        """Get default test file patterns."""
        return ["test_*.py", "*_test.py"]
    
    def supports_coverage(self) -> bool:
        """Check if coverage is supported."""
        return True  # pytest-cov is common
    
    def supports_parallel(self) -> bool:
        """Check if parallel execution is supported."""
        return True  # pytest-xdist
    
    def discover_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> List[Path]:
        """
        Discover Python test files.
        
        Args:
            test_dir: Directory to search
            pattern: File pattern (default: test_*.py)
            
        Returns:
            List of test file paths
        """
        if pattern is None:
            pattern = "test_*.py"
        
        test_path = Path(test_dir)
        
        if not test_path.exists():
            return []
        
        # Find all matching test files
        test_files = []
        
        if test_path.is_file():
            if test_path.match(pattern):
                test_files.append(test_path)
        else:
            # Directory - search recursively
            test_files = list(test_path.rglob(pattern))
        
        # Filter out __pycache__
        test_files = [
            f for f in test_files
            if '__pycache__' not in str(f) and f.suffix == '.py'
        ]
        
        return sorted(test_files)
    
    def count_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> int:
        """
        Count Python test functions.
        
        Args:
            test_dir: Directory containing tests
            pattern: File pattern
            
        Returns:
            Total number of test functions
        """
        test_files = self.discover_tests(test_dir, pattern)
        total_tests = 0
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                tree = ast.parse(code)
                
                # Count test functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith('test_'):
                            total_tests += 1
                    elif isinstance(node, ast.ClassDef):
                        if node.name.startswith('Test'):
                            # Count test methods in test class
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                                    total_tests += 1
            except Exception:
                pass
        
        return total_tests
    
    def build_command(
        self,
        test_dir: str,
        pattern: Optional[str] = None,
        json_report: bool = False,
        json_report_file: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Build pytest command.
        
        Args:
            test_dir: Test directory
            pattern: Test pattern
            json_report: Enable JSON reporting
            json_report_file: JSON report file path
            **kwargs: Additional pytest arguments
            
        Returns:
            Command list
        """
        cmd = ["python", "-m", "pytest"]
        
        # Add test directory
        cmd.append(test_dir)
        
        # Add pattern
        if pattern and pattern != "test_*.py":
            cmd.extend(["-k", pattern])
        
        # Add JSON report if requested
        if json_report:
            cmd.append("--json-report")
            if json_report_file:
                cmd.append(f"--json-report-file={json_report_file}")
        
        # Add short traceback
        cmd.append("--tb=short")
        
        # Add verbose flag
        if self.verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Add custom arguments
        for key, value in kwargs.items():
            if key in ['json_report', 'json_report_file']:
                continue  # Already handled
            if isinstance(value, bool) and value:
                cmd.append(f"--{key}")
            elif value:
                cmd.extend([f"--{key}", str(value)])
        
        return cmd
    
    def run_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None,
        json_report: bool = False,
        json_report_file: Optional[str] = None,
        **kwargs
    ) -> TestResults:
        """
        Run Python tests with pytest.
        
        Args:
            test_dir: Directory containing tests
            pattern: File pattern
            json_report: Enable JSON reporting
            json_report_file: JSON report file path
            **kwargs: Additional pytest arguments
            
        Returns:
            TestResults
        """
        test_path = Path(test_dir)
        
        if not test_path.exists():
            return TestResults(
                total=0,
                errors=1,
                language=self.get_language(),
                framework=self.get_framework()
            )
        
        # Build command
        cmd = self.build_command(
            test_dir,
            pattern,
            json_report=json_report,
            json_report_file=json_report_file,
            **kwargs
        )
        
        if self.verbose:
            print(f"Running: {' '.join(cmd)}")
        
        # Execute tests
        try:
            result = subprocess.run(
                cmd,
                capture_output=self.capture_output,
                text=True,
                cwd=Path.cwd(),
                timeout=300
            )
            
            # Try to parse JSON report if available
            if json_report and json_report_file:
                json_path = Path(json_report_file)
                if json_path.exists():
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                        return self._parse_json_report(json_data)
                    except Exception as e:
                        if self.verbose:
                            print(f"Failed to parse JSON: {e}")
                        # Fall back to text parsing
            
            # Parse text output
            return self._parse_text_output(result)
            
        except subprocess.TimeoutExpired:
            return TestResults(
                total=0,
                errors=1,
                language=self.get_language(),
                framework=self.get_framework(),
                tests=[TestResult(
                    name="execution_timeout",
                    status="error",
                    message="Test execution timed out after 5 minutes"
                )]
            )
        except Exception as e:
            return TestResults(
                total=0,
                errors=1,
                language=self.get_language(),
                framework=self.get_framework(),
                tests=[TestResult(
                    name="execution_error",
                    status="error",
                    message=str(e)
                )]
            )
    
    def _parse_json_report(self, json_data: Dict[str, Any]) -> TestResults:
        """Parse pytest JSON report."""
        results = TestResults(
            language=self.get_language(),
            framework=self.get_framework()
        )
        
        # Extract summary
        summary = json_data.get("summary", {})
        results.passed = summary.get("passed", 0)
        results.failed = summary.get("failed", 0)
        results.skipped = summary.get("skipped", 0)
        results.errors = summary.get("error", 0)
        results.total = summary.get("total", 0)
        results.duration = json_data.get("duration", 0.0)
        
        # Extract individual test results
        tests = json_data.get("tests", [])
        for test in tests:
            test_result = TestResult(
                name=test.get("nodeid", "unknown"),
                status=test.get("outcome", "unknown"),
                duration=test.get("duration", 0.0),
                message=test.get("call", {}).get("longrepr", None)
            )
            results.tests.append(test_result)
        
        return results
    
    def _parse_text_output(self, result: subprocess.CompletedProcess) -> TestResults:
        """Parse pytest text output."""
        output = result.stdout if self.capture_output else ""
        
        results = TestResults(
            language=self.get_language(),
            framework=self.get_framework()
        )
        
        # Parse output for summary
        lines = output.split('\n')
        
        for line in lines:
            if 'passed' in line or 'failed' in line:
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
        
        results.total = results.passed + results.failed + results.skipped + results.errors
        
        # If we couldn't parse, check return code
        if results.total == 0:
            if result.returncode == 0:
                results.passed = 1
                results.total = 1
            else:
                results.errors = 1
                results.total = 1
        
        return results
    
    def validate_test_file(self, test_file: str) -> bool:
        """
        Validate Python test file.
        
        Args:
            test_file: Path to test file
            
        Returns:
            True if valid
        """
        try:
            with open(test_file, 'r') as f:
                code = f.read()
            
            # Try to parse
            tree = ast.parse(code)
            
            # Check for test functions
            has_tests = any(
                isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
                for node in ast.walk(tree)
            )
            
            return has_tests
        except Exception:
            return False

"""
Python Test Runner (pytest-based).

Implements BaseTestRunner for Python projects using pytest.
"""

import subprocess
import json
import ast
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base_runner import BaseTestRunner, TestResults, TestResult


class PythonTestRunner(BaseTestRunner):
    """An automated test runner for Python projects using the Pytest framework.

    This runner handles environment setup, test discovery, execution, and
    result parsing. it supports cross-platform execution and can produce
    structured JSON reports for further analysis.
    """
    
    def __init__(self, verbose: bool = False, capture_output: bool = True, project_dir: Optional[str] = None):
        """
        Initialize Python test runner.
        
        Args:
            verbose: Print verbose output
            capture_output: Capture test output
            project_dir: Root directory of the project
        """
        super().__init__(verbose)
        self.capture_output = capture_output
        self.project_dir = project_dir
    
    # ... (get_language, get_framework, etc. remain the same)

    
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
        """Estimate the total number of test functions across all discovered files.

        Uses AST parsing to accurately count functions that start with 'test'
        or are within 'Test' classes, without needing to execute the code.

        Args:
            test_dir (str): The directory containing test files.
            pattern (Optional[str]): A glob pattern for file filtering.

        Returns:
            int: The total count of identified test functions.
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
        """Construct the full pytest command-line call.

        Args:
            test_dir (str): Targeted test directory.
            pattern (Optional[str]): File filtering pattern.
            json_report (bool): If True, appends JSON reporting flags.
            json_report_file (Optional[str]): Path for the JSON output.
            **kwargs: Extra flags (e.g., 'verbose', 'junitxml').

        Returns:
            List[str]: The complete command as a list of strings for `subprocess.run`.
        """
        cmd = [sys.executable, "-m", "pytest"]
        
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
        
        # Always continue past collection errors so valid tests still run
        cmd.append("--continue-on-collection-errors")

        # Add short traceback
        cmd.append("--tb=short")
        
        # Always use verbose flag to enable output parsing
        cmd.append("-v")
        
        # Add custom arguments
        for key, value in kwargs.items():
            if key in ['json_report', 'json_report_file']:
                continue  # Already handled
            if isinstance(value, bool) and value:
                cmd.append(f"--{key}")
            elif value:
                cmd.extend([f"--{key}", str(value)])
        
        return cmd
    
    def _inject_conftest(self, test_dir: Path) -> None:
        """Automatically create a conftest.py file to handle cross-project imports.

        This ensures that when pytest runs, the source code directory is
        correctly added to `sys.path`, allowing tests to import the project
        modules regardless of the current working directory.

        Args:
            test_dir (Path): The directory where the conftest.py should be created.
        """
        conftest_path = test_dir / "conftest.py"
        if conftest_path.exists():
            return
            
        try:
            # Calculate the tool root (TestGen-AI installation directory)
            tool_root = Path(__file__).resolve().parent.parent.parent.parent  # src/testgen/core/ → project
            tool_root_str = str(tool_root).replace('\\', '/')

            # Calculate the analyzed project directory (self.project_dir or cwd)
            project_root = Path(self.project_dir).resolve() if self.project_dir else Path.cwd().resolve()
            project_root_str = str(project_root).replace('\\', '/')
            
            content = f"""import sys
from pathlib import Path

# Add the TestGen-AI tool root to sys.path (for full package imports like examples.complex_app.main)
_tool_root = r"{tool_root_str}"
if _tool_root not in sys.path:
    sys.path.insert(0, _tool_root)

# Add the analyzed project directory to sys.path (for short imports like 'from utils.string_utils import ...')
# This file sits at: <project>/TestGen-AI/tests/<run>/conftest.py — project root is 3 levels up.
_conftest_dir = Path(__file__).parent
_project_root = _conftest_dir.parent.parent.parent  # <run>/ → tests/ → TestGen-AI/ → project/
_project_root_str = str(_project_root)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)
"""
            conftest_path.write_text(content, encoding='utf-8')
            if self.verbose:
                print(f"Injected conftest.py at {conftest_path}")
                
        except Exception as e:
            if self.verbose:
                print(f"Failed to inject conftest.py: {e}")

    def run_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None,
        json_report: bool = False,
        json_report_file: Optional[str] = None,
        **kwargs
    ) -> TestResults:
        """Execute Python tests using pytest.

        This method orchestrates the entire test execution flow: injecting
        path configurations, building the command, managing the execution 
        environment, and parsing the results back into a structured format.

        Args:
            test_dir (str): The directory where tests are located.
            pattern (Optional[str]): A glob pattern to filter test files.
                Defaults to None (uses standard pytest discovery).
            json_report (bool): Whether to request a JSON report from pytest.
                Defaults to False.
            json_report_file (Optional[str]): Path where the JSON report
                should be saved. Required if `json_report` is True.
            **kwargs: Additional keyword arguments passed directly to the
                underlying `pytest` command construction.

        Returns:
            TestResults: An object containing aggregated counts and individual
                test details.
        """
        test_path = Path(test_dir)
        
        # Inject conftest.py to ensure the project modules are importable
        if test_path.exists():
            self._inject_conftest(test_path)
        
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
            # Set up environment with PYTHONPATH to include project root
            import os
            execute_env = os.environ.copy()
            if self.project_dir:
                project_path = str(Path(self.project_dir).resolve())
                if 'PYTHONPATH' in execute_env:
                    execute_env['PYTHONPATH'] = f"{project_path}{os.pathsep}{execute_env['PYTHONPATH']}"
                else:
                    execute_env['PYTHONPATH'] = project_path

            result = subprocess.run(
                cmd,
                capture_output=self.capture_output,
                text=True,
                cwd=Path.cwd(),
                timeout=300,
                env=execute_env
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
        """Parse the raw JSON output from the pytest-json-report plugin.

        Args:
            json_data (Dict[str, Any]): The deserialized JSON report.

        Returns:
            TestResults: A structured summary of the execution.
        """
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
        """Heuristically parse the standard text output from a pytest run.

        Used as a fallback when JSON reporting is unavailable. Extracts pass/fail
        counts and high-level execution status.

        Args:
            result (subprocess.CompletedProcess): The execution result.

        Returns:
            TestResults: A best-effort summary of the test run.
        """
        """Parse pytest text output."""
        output = result.stdout if self.capture_output else ""
        stderr_output = result.stderr if self.capture_output else ""
        combined = output + "\n" + stderr_output

        results = TestResults(
            language=self.get_language(),
            framework=self.get_framework()
        )

        import re

        # -- Individual test lines: test_file.py::test_name PASSED/FAILED/SKIPPED/ERROR --
        test_pattern = r'([\w/\\.:+-]+\.py)::(\S+)\s+(PASSED|FAILED|SKIPPED|ERROR)'
        for match in re.finditer(test_pattern, combined):
            file_path, test_name, status = match.groups()
            results.tests.append(TestResult(
                name=f"{Path(file_path).name}::{test_name}",
                status=status.lower(),
                duration=0.0,
                message=""
            ))

        # -- Collection errors: "ERROR collecting test_something.py" --
        collection_pattern = r'ERROR collecting ([\w/\\.-]+\.py)'
        for match in re.finditer(collection_pattern, combined):
            file_path = match.group(1)
            results.tests.append(TestResult(
                name=f"{Path(file_path).name}::COLLECTION_ERROR",
                status="error",
                duration=0.0,
                message="Failed to collect (import/syntax error — run with --debug to see details)"
            ))

        # -- Summary line: "N passed", "N failed", etc. --
        passed_match  = re.search(r'(\d+) passed',  combined)
        failed_match  = re.search(r'(\d+) failed',  combined)
        skipped_match = re.search(r'(\d+) skipped', combined)
        error_match   = re.search(r'(\d+) error',   combined)
        duration_match = re.search(r'in ([\d.]+)s', combined)

        if passed_match:   results.passed   = int(passed_match.group(1))
        if failed_match:   results.failed   = int(failed_match.group(1))
        if skipped_match:  results.skipped  = int(skipped_match.group(1))
        if error_match:    results.errors   = int(error_match.group(1))
        if duration_match: results.duration = float(duration_match.group(1))

        # Fall back to counting parsed test lines when summary is absent
        if results.passed == results.failed == results.skipped == results.errors == 0 and results.tests:
            for t in results.tests:
                if t.status == 'passed':  results.passed  += 1
                elif t.status == 'failed': results.failed += 1
                elif t.status == 'skipped': results.skipped += 1
                else:                      results.errors  += 1

        results.total = results.passed + results.failed + results.skipped + results.errors
        return results
    
    def validate_test_file(self, test_file: str) -> bool:
        """Check if a file is a valid Python test file using static analysis.

        Verifies that the file exists and is syntactically correct Python.

        Args:
            test_file (str): Path to the file to validate.

        Returns:
            bool: True if the file is a valid, parsable Python file.
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

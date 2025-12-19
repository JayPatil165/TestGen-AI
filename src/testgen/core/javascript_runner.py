"""
JavaScript/TypeScript Test Runner (Jest-based).

Implements BaseTestRunner for JavaScript/TypeScript projects using Jest.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base_runner import BaseTestRunner, TestResults, TestResult


class JavaScriptTestRunner(BaseTestRunner):
    """
    Test runner for JavaScript/TypeScript projects using Jest.
    
    Inherits from BaseTestRunner and implements Jest-specific logic.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize JavaScript test runner.
        
        Args:
            verbose: Print verbose output
        """
        super().__init__(verbose)
        self.is_typescript = False
    
    def get_language(self) -> str:
        """Get language name."""
        return "typescript" if self.is_typescript else "javascript"
    
    def get_framework(self) -> str:
        """Get test framework name."""
        return "jest"
    
    def get_test_patterns(self) -> List[str]:
        """Get default test file patterns."""
        if self.is_typescript:
            return ["*.test.ts", "*.spec.ts", "**/__tests__/**/*.ts"]
        return ["*.test.js", "*.spec.js", "**/__tests__/**/*.js"]
    
    def supports_coverage(self) -> bool:
        """Check if coverage is supported."""
        return True  # Jest has built-in coverage
    
    def supports_parallel(self) -> bool:
        """Check if parallel execution is supported."""
        return True  # Jest runs tests in parallel by default
    
    def discover_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> List[Path]:
        """
        Discover JavaScript/TypeScript test files.
        
        Args:
            test_dir: Directory to search
            pattern: File pattern
            
        Returns:
            List of test file paths
        """
        test_path = Path(test_dir)
        
        if not test_path.exists():
            return []
        
        # Check if TypeScript
        if (test_path / "tsconfig.json").exists():
            self.is_typescript = True
        
        # Default patterns
        if pattern is None:
            patterns = self.get_test_patterns()
        else:
            patterns = [pattern]
        
        test_files = []
        for pat in patterns:
            if test_path.is_file():
                if test_path.match(pat):
                    test_files.append(test_path)
            else:
                test_files.extend(list(test_path.rglob(pat)))
        
        # Filter out node_modules
        test_files = [
            f for f in test_files
            if 'node_modules' not in str(f)
        ]
        
        return sorted(set(test_files))
    
    def count_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None
    ) -> int:
        """
        Count JavaScript/TypeScript test cases.
        
        Args:
            test_dir: Directory containing tests
            pattern: File pattern
            
        Returns:
            Estimated number of tests
        """
        test_files = self.discover_tests(test_dir, pattern)
        total_tests = 0
        
        # For JS/TS, we count test functions by looking for test/it keywords
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count test/it/describe blocks
                total_tests += content.count("test(")
                total_tests += content.count("it(")
                total_tests += content.count("test.skip(")
                total_tests += content.count("it.skip(")
            except Exception:
                pass
        
        return total_tests
    
    def build_command(
        self,
        test_dir: str,
        pattern: Optional[str] = None,
        json_output: bool = True,
        **kwargs
    ) -> List[str]:
        """
        Build Jest command.
        
        Args:
            test_dir: Test directory
            pattern: Test pattern
            json_output: Enable JSON output
            **kwargs: Additional Jest arguments
            
        Returns:
            Command list
        """
        # Check if npm or yarn
        package_json = Path(test_dir).parent / "package.json"
        if not package_json.exists():
            package_json = Path(test_dir) / "package.json"
        
        # Determine command
        if (Path(test_dir) / "yarn.lock").exists():
            cmd = ["yarn", "test"]
        else:
            cmd = ["npm", "test", "--"]
        
        # Add JSON output
        if json_output:
            cmd.append("--json")
        
        # Add pattern
        if pattern:
            cmd.append(pattern)
        
        # Add verbose
        if self.verbose:
            cmd.append("--verbose")
        
        # Add custom arguments
        for key, value in kwargs.items():
            if isinstance(value, bool) and value:
                cmd.append(f"--{key}")
            elif value:
                cmd.extend([f"--{key}", str(value)])
        
        return cmd
    
    def run_tests(
        self,
        test_dir: str,
        pattern: Optional[str] = None,
        **kwargs
    ) -> TestResults:
        """
        Run JavaScript/TypeScript tests with Jest.
        
        Args:
            test_dir: Directory containing tests
            pattern: Test pattern
            **kwargs: Additional Jest arguments
            
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
        cmd = self.build_command(test_dir, pattern, **kwargs)
        
        if self.verbose:
            print(f"Running: {' '.join(cmd)}")
        
        # Execute tests
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=test_path if test_path.is_dir() else test_path.parent,
                timeout=300
            )
            
            # Try to parse JSON output
            try:
                output = result.stdout
                # Jest outputs JSON when --json flag is used
                if output.strip().startswith('{'):
                    json_data = json.loads(output)
                    return self._parse_json_output(json_data)
            except Exception as e:
                if self.verbose:
                    print(f"Failed to parse JSON: {e}")
            
            # Fall back to text parsing
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
    
    def _parse_json_output(self, json_data: Dict[str, Any]) -> TestResults:
        """Parse Jest JSON output."""
        results = TestResults(
            language=self.get_language(),
            framework=self.get_framework()
        )
        
        # Extract summary
        results.total = json_data.get("numTotalTests", 0)
        results.passed = json_data.get("numPassedTests", 0)
        results.failed = json_data.get("numFailedTests", 0)
        results.skipped = json_data.get("numPendingTests", 0)
        
        # Duration (Jest reports in ms)
        duration_ms = json_data.get("testResults", [{}])[0].get("endTime", 0) - \
                      json_data.get("testResults", [{}])[0].get("startTime", 0)
        results.duration = duration_ms / 1000.0
        
        # Extract individual test results
        test_results = json_data.get("testResults", [])
        for test_file in test_results:
            for assertion in test_file.get("assertionResults", []):
                test_result = TestResult(
                    name=f"{assertion.get('ancestorTitles', [''])[0]} {assertion.get('title', '')}",
                    status=assertion.get("status", "unknown"),
                    duration=assertion.get("duration", 0) / 1000.0,
                    message=assertion.get("failureMessages", [None])[0] if assertion.get("failureMessages") else None
                )
                results.tests.append(test_result)
        
        return results
    
    def _parse_text_output(self, result: subprocess.CompletedProcess) -> TestResults:
        """Parse Jest text output."""
        output = result.stdout
        
        results = TestResults(
            language=self.get_language(),
            framework=self.get_framework()
        )
        
        # Jest outputs summary at the end
        lines = output.split('\n')
        
        for line in lines:
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
        Validate JavaScript/TypeScript test file.
        
        Args:
            test_file: Path to test file
            
        Returns:
            True if valid
        """
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Check for test functions
            has_tests = (
                'test(' in content or
                'it(' in content or
                'describe(' in content
            )
            
            return has_tests
        except Exception:
            return False

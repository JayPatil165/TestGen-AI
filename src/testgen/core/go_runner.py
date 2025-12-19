"""
Go Test Runner.

Implements BaseTestRunner for Go projects using built-in testing package.
"""

import subprocess
from pathlib import Path
from typing import List, Optional

from .base_runner import BaseTestRunner, TestResults, TestResult


class GoTestRunner(BaseTestRunner):
    """Test runner for Go projects using built-in testing."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
    
    def get_language(self) -> str:
        return "go"
    
    def get_framework(self) -> str:
        return "testing"
    
    def get_test_patterns(self) -> List[str]:
        return ["*_test.go"]
    
    def supports_coverage(self) -> bool:
        return True  # go test -cover
    
    def supports_parallel(self) -> bool:
        return True  # t.Parallel()
    
    def discover_tests(self, test_dir: str, pattern: Optional[str] = None) -> List[Path]:
        if pattern is None:
            pattern = "*_test.go"
        
        test_path = Path(test_dir)
        if not test_path.exists():
            return []
        
        test_files = list(test_path.rglob(pattern))
        return sorted(test_files)
    
    def count_tests(self, test_dir: str, pattern: Optional[str] = None) -> int:
        test_files = self.discover_tests(test_dir, pattern)
        total = 0
        
        for test_file in test_files:
            try:
                content = test_file.read_text()
                # Count Test functions
                for line in content.split('\n'):
                    if line.strip().startswith('func Test'):
                        total += 1
            except:
                pass
        
        return total
    
    def build_command(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> List[str]:
        cmd = ["go", "test"]
        
        if self.verbose:
            cmd.append("-v")
        
        # Add package path
        cmd.append("./...")
        
        return cmd
    
    def run_tests(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> TestResults:
        cmd = self.build_command(test_dir, pattern, **kwargs)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=test_dir,
                timeout=300
            )
            return self._parse_output(result)
        except subprocess.TimeoutExpired:
            return TestResults(total=0, errors=1, language=self.get_language(), framework=self.get_framework())
        except Exception as e:
            return TestResults(total=0, errors=1, language=self.get_language(), framework=self.get_framework())
    
    def _parse_output(self, result: subprocess.CompletedProcess) -> TestResults:
        results = TestResults(language=self.get_language(), framework=self.get_framework())
        
        output = result.stdout
        
        # Parse go test output
        for line in output.split('\n'):
            if line.startswith('PASS'):
                results.passed += 1
            elif line.startswith('FAIL'):
                results.failed += 1
            elif line.startswith('SKIP'):
                results.skipped += 1
        
        results.total = results.passed + results.failed + results.skipped
       
        # Check exit code
        if result.returncode == 0:
            results.passed = max(results.passed, 1)
            results.total = max(results.total, 1)
        
        return results
    
    def validate_test_file(self, test_file: str) -> bool:
        try:
            content = Path(test_file).read_text()
            return test_file.endswith('_test.go') and 'func Test' in content
        except:
            return False

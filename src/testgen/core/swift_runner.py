"""Swift Test Runner (XCTest)."""

import subprocess
from pathlib import Path
from typing import List, Optional
from .base_runner import BaseTestRunner, TestResults, TestResult


class SwiftTestRunner(BaseTestRunner):
    """Test runner for Swift projects using swift test."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
    
    def get_language(self) -> str:
        return "swift"
    
    def get_framework(self) -> str:
        return "xctest"
    
    def get_test_patterns(self) -> List[str]:
        return ["*Tests.swift"]
    
    def supports_coverage(self) -> bool:
        return True
    
    def supports_parallel(self) -> bool:
        return True
    
    def discover_tests(self, test_dir: str, pattern: Optional[str] = None) -> List[Path]:
        if pattern is None:
            pattern = "*Tests.swift"
        test_path = Path(test_dir)
        if not test_path.exists():
            return []
        return sorted(list(test_path.rglob(pattern)))
    
    def count_tests(self, test_dir: str, pattern: Optional[str] = None) -> int:
        test_files = self.discover_tests(test_dir, pattern)
        total = 0
        for test_file in test_files:
            try:
                content = test_file.read_text()
                for line in content.split('\n'):
                    if 'func test' in line:
                        total += 1
            except:
                pass
        return total
    
    def build_command(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> List[str]:
        cmd = ["swift", "test"]
        if self.verbose:
            cmd.append("--verbose")
        return cmd
    
    def run_tests(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> TestResults:
        cmd = self.build_command(test_dir, pattern, **kwargs)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=test_dir, timeout=300)
            return self._parse_output(result)
        except:
            return TestResults(total=0, errors=1, language=self.get_language(), framework=self.get_framework())
    
    def _parse_output(self, result: subprocess.CompletedProcess) -> TestResults:
        results = TestResults(language=self.get_language(), framework=self.get_framework())
        output = result.stdout
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
        if results.total == 0 and result.returncode == 0:
            results.passed = results.total = 1
        return results
    
    def validate_test_file(self, test_file: str) -> bool:
        try:
            content = Path(test_file).read_text()
            return 'XCTest' in content and 'func test' in content
        except:
            return False

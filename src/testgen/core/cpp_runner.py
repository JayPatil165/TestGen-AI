"""C++ Test Runner (Google Test)."""

import subprocess
from pathlib import Path
from typing import List, Optional
from .base_runner import BaseTestRunner, TestResults, TestResult


class CppTestRunner(BaseTestRunner):
    """Test runner for C++ projects using Google Test."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
    
    def get_language(self) -> str:
        return "cpp"
    
    def get_framework(self) -> str:
        return "gtest"
    
    def get_test_patterns(self) -> List[str]:
        return ["*_test.cpp", "*Test.cpp"]
    
    def supports_coverage(self) -> bool:
        return True
    
    def supports_parallel(self) -> bool:
        return True
    
    def discover_tests(self, test_dir: str, pattern: Optional[str] = None) -> List[Path]:
        if pattern is None:
            pattern = "*_test.cpp"
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
                total += content.count("TEST(") + content.count("TEST_F(")
            except:
                pass
        return total
    
    def build_command(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> List[str]:
        # Assume tests are built and executable exists
        return ["./run_tests"]  # Or ctest, make test, etc.
    
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
            if '[  PASSED  ]' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit() and 'test' in line.lower():
                        results.passed = int(part)
            elif '[  FAILED  ]' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        results.failed = int(part)
        results.total = results.passed + results.failed
        if results.total == 0 and result.returncode == 0:
            results.passed = results.total = 1
        return results
    
    def validate_test_file(self, test_file: str) -> bool:
        try:
            content = Path(test_file).read_text()
            return 'TEST(' in content or 'TEST_F(' in content
        except:
            return False

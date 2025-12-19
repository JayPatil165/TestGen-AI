"""CSS Test Runner (Stylelint)."""

import subprocess
from pathlib import Path
from typing import List, Optional
from .base_runner import BaseTestRunner, TestResults, TestResult


class CSSTestRunner(BaseTestRunner):
    """Test runner for CSS using Stylelint."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
    
    def get_language(self) -> str:
        return "css"
    
    def get_framework(self) -> str:
        return "stylelint"
    
    def get_test_patterns(self) -> List[str]:
        return ["*.css", "*.scss"]
    
    def supports_coverage(self) -> bool:
        return False
    
    def supports_parallel(self) -> bool:
        return False
    
    def discover_tests(self, test_dir: str, pattern: Optional[str] = None) -> List[Path]:
        if pattern is None:
            pattern = "*.css"
        test_path = Path(test_dir)
        if not test_path.exists():
            return []
        return sorted(list(test_path.rglob(pattern)))
    
    def count_tests(self, test_dir: str, pattern: Optional[str] = None) -> int:
        # For CSS, count files as "tests"
        test_files = self.discover_tests(test_dir, pattern)
        return len(test_files)
    
    def build_command(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> List[str]:
        return ["npx", "stylelint", "**/*.css"]
    
    def run_tests(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> TestResults:
        cmd = self.build_command(test_dir, pattern, **kwargs)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=test_dir, timeout=300)
            return self._parse_output(result)
        except:
            return TestResults(total=0, errors=1, language=self.get_language(), framework=self.get_framework())
    
    def _parse_output(self, result: subprocess.CompletedProcess) -> TestResults:
        results = TestResults(language=self.get_language(), framework=self.get_framework())
        # Stylelint returns 0 for pass, non-zero for lint errors
        if result.returncode == 0:
            results.passed = 1
            results.total = 1
        else:
            results.failed = 1
            results.total = 1
        return results
    
    def validate_test_file(self, test_file: str) -> bool:
        try:
            return test_file.endswith('.css') or test_file.endswith('.scss')
        except:
            return False

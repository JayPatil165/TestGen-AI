"""PHP Test Runner (PHPUnit)."""

import subprocess
from pathlib import Path
from typing import List, Optional
from .base_runner import BaseTestRunner, TestResults, TestResult


class PHPTestRunner(BaseTestRunner):
    """Test runner for PHP projects using PHPUnit."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
    
    def get_language(self) -> str:
        return "php"
    
    def get_framework(self) -> str:
        return "phpunit"
    
    def get_test_patterns(self) -> List[str]:
        return ["*Test.php"]
    
    def supports_coverage(self) -> bool:
        return True
    
    def supports_parallel(self) -> bool:
        return True
    
    def discover_tests(self, test_dir: str, pattern: Optional[str] = None) -> List[Path]:
        if pattern is None:
            pattern = "*Test.php"
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
                    if 'function test' in line or '@test' in line:
                        total += 1
            except:
                pass
        return total
    
    def build_command(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> List[str]:
        cmd = ["phpunit"]
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
        if results.total == 0 and result.returncode == 0:
            results.passed = results.total = 1
        return results
    
    def validate_test_file(self, test_file: str) -> bool:
        try:
            content = Path(test_file).read_text()
            return 'extends TestCase' in content or 'function test' in content
        except:
            return False

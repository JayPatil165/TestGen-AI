"""Ruby Test Runner (RSpec)."""

import subprocess
from pathlib import Path
from typing import List, Optional
from .base_runner import BaseTestRunner, TestResults, TestResult


class RubyTestRunner(BaseTestRunner):
    """Test runner for Ruby projects using RSpec."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
    
    def get_language(self) -> str:
        return "ruby"
    
    def get_framework(self) -> str:
        return "rspec"
    
    def get_test_patterns(self) -> List[str]:
        return ["*_spec.rb", "test_*.rb"]
    
    def supports_coverage(self) -> bool:
        return True
    
    def supports_parallel(self) -> bool:
        return True
    
    def discover_tests(self, test_dir: str, pattern: Optional[str] = None) -> List[Path]:
        if pattern is None:
            pattern = "*_spec.rb"
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
                total += content.count("it ") + content.count("it(")
            except:
                pass
        return total
    
    def build_command(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> List[str]:
        cmd = ["rspec"]
        if self.verbose:
            cmd.append("--format", "documentation")
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
        if results.total == 0 and result.returncode == 0:
            results.passed = results.total = 1
        return results
    
    def validate_test_file(self, test_file: str) -> bool:
        try:
            content = Path(test_file).read_text()
            return 'RSpec' in content or 'describe' in content
        except:
            return False

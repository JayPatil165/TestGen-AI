"""
Java Test Runner (JUnit-based).

Implements BaseTestRunner for Java projects using JUnit.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Optional

from .base_runner import BaseTestRunner, TestResults, TestResult


class JavaTestRunner(BaseTestRunner):
    """Test runner for Java projects using JUnit."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
    
    def get_language(self) -> str:
        return "java"
    
    def get_framework(self) -> str:
        return "junit"
    
    def get_test_patterns(self) -> List[str]:
        return ["*Test.java", "*Tests.java"]
    
    def supports_coverage(self) -> bool:
        return True  # JaCoCo
    
    def supports_parallel(self) -> bool:
        return True
    
    def discover_tests(self, test_dir: str, pattern: Optional[str] = None) -> List[Path]:
        if pattern is None:
            pattern = "*Test.java"
        
        test_path = Path(test_dir)
        if not test_path.exists():
            return []
        
        test_files = list(test_path.rglob(pattern))
        return sorted([f for f in test_files if 'target' not in str(f)])
    
    def count_tests(self, test_dir: str, pattern: Optional[str] = None) -> int:
        test_files = self.discover_tests(test_dir, pattern)
        total =0
        
        for test_file in test_files:
            try:
                content = test_file.read_text()
                # Count @Test annotations
                total += content.count("@Test")
            except:
                pass
        
        return total
    
    def build_command(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> List[str]:
        # Check for Maven or Gradle
        project_root = Path(test_dir).parent
        
        if (project_root / "pom.xml").exists():
            return ["mvn", "test"]
        elif (project_root / "build.gradle").exists() or (project_root / "build.gradle.kts").exists():
            return ["gradle", "test"]
        else:
            return ["mvn", "test"]  # Default
    
    def run_tests(self, test_dir: str, pattern: Optional[str] = None, **kwargs) -> TestResults:
        cmd = self.build_command(test_dir, pattern, **kwargs)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return self._parse_output(result)
        except subprocess.TimeoutExpired:
            return TestResults(total=0, errors=1, language=self.get_language(), framework=self.get_framework())
        except Exception as e:
            return TestResults(total=0, errors=1, language=self.get_language(), framework=self.get_framework())
    
    def _parse_output(self, result: subprocess.CompletedProcess) -> TestResults:
        results = TestResults(language=self.get_language(), framework=self.get_framework())
        
        output = result.stdout
        
        # Parse Maven/Gradle output
        for line in output.split('\n'):
            if 'Tests run:' in line:
                parts = line.split(',')
                for part in parts:
                    if 'Tests run:' in part:
                        results.total = int(part.split(':')[1].strip())
                    elif 'Failures:' in part:
                        results.failed = int(part.split(':')[1].strip())
                    elif 'Errors:' in part:
                        results.errors = int(part.split(':')[1].strip())
                    elif 'Skipped:' in part:
                        results.skipped = int(part.split(':')[1].strip())
        
        results.passed = results.total - results.failed - results.errors - results.skipped
        return results
    
    def validate_test_file(self, test_file: str) -> bool:
        try:
            content = Path(test_file).read_text()
            return '@Test' in content or 'Test' in Path(test_file).stem
        except:
            return False

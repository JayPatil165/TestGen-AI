"""
Universal Auto-Test Runner for TestGen AI.

Automatically runs tests after generation across ALL 14 programming languages.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import subprocess
import sys

from .language_config import Language, get_language_config
from .runner_factory import TestRunnerFactory, create_test_runner
from .feedback_system import UniversalFeedbackSystem, get_feedback_system


@dataclass
class AutoRunResult:
    """Result of auto-running tests."""
    
    test_file: Path
    language: Language
    success: bool
    output: str
    error: Optional[str] = None
    duration: float = 0.0
    tests_passed: int = 0
    tests_failed: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class UniversalAutoRunner:
    """
    Universal auto-test runner supporting ALL 14 programming languages.
    
    Automatically runs generated tests and displays results.
    """
    
    def __init__(
        self,
        auto_run: bool = False,
        feedback_system: Optional[UniversalFeedbackSystem] = None
    ):
        """
        Initialize auto-runner.
        
        Args:
            auto_run: Whether to auto-run tests
            feedback_system: Feedback system for output
        """
        self.auto_run = auto_run
        self.feedback = feedback_system or get_feedback_system()
        self.run_history: list[AutoRunResult] = []
    
    def should_auto_run(self) -> bool:
        """Check if auto-run is enabled."""
        return self.auto_run
    
    def run_test_file(
        self,
        test_file: Path,
        language: Language
    ) -> AutoRunResult:
        """
        Run a test file after generation.
        
        Args:
            test_file: Test file to run
            language: Programming language
            
        Returns:
            Auto-run result
        """
        start_time = datetime.now()
        
        try:
            # Show feedback
            self.feedback._show_message(
                "progress",
                f"🏃 Running tests: {test_file.name}...",
                language=language.value
            )
            
            # Run tests using appropriate runner
            result = self._execute_tests(test_file, language)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse results
            auto_result = AutoRunResult(
                test_file=test_file,
                language=language,
                success=result.get('success', False),
                output=result.get('output', ''),
                error=result.get('error'),
                duration=duration,
                tests_passed=result.get('passed', 0),
                tests_failed=result.get('failed', 0)
            )
            
            # Show results
            self._display_results(auto_result)
            
            self.run_history.append(auto_result)
            return auto_result
            
        except Exception as e:
            error_result = AutoRunResult(
                test_file=test_file,
                language=language,
                success=False,
                output="",
                error=str(e)
            )
            
            self.feedback.error_occurred(
                f"Failed to run tests: {e}",
                file_path=test_file,
                language=language.value
            )
            
            self.run_history.append(error_result)
            return error_result
    
    def _execute_tests(
        self,
        test_file: Path,
        language: Language
    ) -> Dict[str, Any]:
        """
        Execute tests using language-specific runner.
        
        Args:
            test_file: Test file path
            language: Programming language
            
        Returns:
            Execution result dict
        """
        # Get test command for language
        command = self._get_test_command(test_file, language)
        
        if not command:
            return {
                'success': False,
                'error': f'No test command configured for {language.value}'
            }
        
        try:
            # Run command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=Path.cwd()
            )
            
            # Parse output
            passed, failed = self._parse_test_output(
                result.stdout + result.stderr,
                language
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr,
                'passed': passed,
                'failed': failed
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Test execution timed out (30s)'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def _get_test_command(
        self,
        test_file: Path,
        language: Language
    ) -> Optional[list[str]]:
        """
        Get test command for a language.
        
        Args:
            test_file: Test file path
            language: Programming language
            
        Returns:
            Command as list of strings
        """
        file_str = str(test_file)
        
        if language == Language.PYTHON:
            return ['pytest', file_str, '-v']
        
        elif language == Language.JAVASCRIPT:
            return ['npm', 'test', '--', file_str]
        
        elif language == Language.TYPESCRIPT:
            return ['npm', 'test', '--', file_str]
        
        elif language == Language.JAVA:
            # Assume Maven or Gradle
            if Path('pom.xml').exists():
                return ['mvn', 'test']
            elif Path('build.gradle').exists():
                return ['gradle', 'test']
            return None
        
        elif language == Language.GO:
            return ['go', 'test', file_str]
        
        elif language == Language.CSHARP:
            return ['dotnet', 'test', file_str]
        
        elif language == Language.RUBY:
            return ['rspec', file_str]
        
        elif language == Language.RUST:
            return ['cargo', 'test']
        
        elif language == Language.PHP:
            return ['./vendor/bin/phpunit', file_str]
        
        elif language == Language.SWIFT:
            return ['swift', 'test']
        
        elif language == Language.KOTLIN:
            return ['gradle', 'test']
        
        elif language == Language.CPP:
            # Assume compiled test binary exists
            test_binary = test_file.with_suffix('')
            if test_binary.exists():
                return [str(test_binary)]
            return None
        
        else:
            return None
    
    def _parse_test_output(
        self,
        output: str,
        language: Language
    ) -> tuple[int, int]:
        """
        Parse test output to get pass/fail counts.
        
        Args:
            output: Test output
            language: Programming language
            
        Returns:
            Tuple of (passed, failed)
        """
        passed = 0
        failed = 0
        
        # Language-specific parsing patterns
        if language == Language.PYTHON:
            # pytest: "5 passed, 2 failed"
            import re
            if match := re.search(r'(\d+) passed', output):
                passed = int(match.group(1))
            if match := re.search(r'(\d+) failed', output):
                failed = int(match.group(1))
        
        elif language == Language.JAVASCRIPT or language == Language.TYPESCRIPT:
            # Jest: "Tests: 2 failed, 5 passed, 7 total"
            import re
            if match := re.search(r'(\d+) passed', output):
                passed = int(match.group(1))
            if match := re.search(r'(\d+) failed', output):
                failed = int(match.group(1))
        
        elif language == Language.JAVA:
            # JUnit: "Tests run: 7, Failures: 2"
            import re
            if match := re.search(r'Tests run: (\d+)', output):
                total = int(match.group(1))
                if fail_match := re.search(r'Failures: (\d+)', output):
                    failed = int(fail_match.group(1))
                    passed = total - failed
        
        elif language == Language.GO:
            # Go: "PASS" or "FAIL"
            if 'PASS' in output:
                passed = 1
            elif 'FAIL' in output:
                failed = 1
        
        # Add more language-specific patterns as needed
        
        return (passed, failed)
    
    def _display_results(self, result: AutoRunResult) -> None:
        """
        Display test results.
        
        Args:
            result: Auto-run result
        """
        if result.success:
            message = f"✅ Tests passed: {result.test_file.name}"
            if result.tests_passed > 0:
                message += f" ({result.tests_passed} passed"
                if result.tests_failed > 0:
                    message += f", {result.tests_failed} failed"
                message += f", {result.duration:.2f}s)"
            
            self.feedback._show_message(
                "success",
                message,
                language=result.language.value,
                file_path=result.test_file
            )
        else:
            message = f"❌ Tests failed: {result.test_file.name}"
            if result.tests_failed > 0:
                message += f" ({result.tests_failed} failed"
                if result.tests_passed > 0:
                    message += f", {result.tests_passed} passed"
                message += ")"
            
            if result.error:
                message += f"\n   Error: {result.error}"
            
            self.feedback._show_message(
                "error",
                message,
                language=result.language.value,
                file_path=result.test_file
            )
            
            # Show brief output if available
            if result.output and self.feedback.verbose:
                lines = result.output.strip().split('\n')
                if len(lines) > 10:
                    # Show first 5 and last 5 lines
                    preview = '\n'.join(lines[:5] + ['...'] + lines[-5:])
                else:
                    preview = result.output
                
                print(f"\n{preview}\n")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get auto-run statistics."""
        total = len(self.run_history)
        successful = sum(1 for r in self.run_history if r.success)
        failed = total - successful
        
        total_passed = sum(r.tests_passed for r in self.run_history)
        total_failed = sum(r.tests_failed for r in self.run_history)
        
        by_language = {}
        for result in self.run_history:
            lang = result.language.value
            by_language[lang] = by_language.get(lang, 0) + 1
        
        return {
            'total_runs': total,
            'successful_runs': successful,
            'failed_runs': failed,
            'total_tests_passed': total_passed,
            'total_tests_failed': total_failed,
            'by_language': by_language
        }


# Convenience function
def create_auto_runner(
    auto_run: bool = False,
    feedback_system: Optional[UniversalFeedbackSystem] = None
) -> UniversalAutoRunner:
    """Create auto-runner instance."""
    return UniversalAutoRunner(auto_run, feedback_system)

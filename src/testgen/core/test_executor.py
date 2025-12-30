"""
Universal Test Executor with Specialized Configurations.

Runs tests with appropriate settings based on test type and language:
- UI/E2E tests: headless mode, screenshots, timeouts
- Unit tests: fast, parallel
- Integration tests: fixtures, database setup
- Performance tests: iterations, profiling
- etc.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .test_detector import UniversalTestTypeDetector, TestType
from .base_runner import BaseTestRunner, TestResults


@dataclass
class TestExecutionConfig:
    """
    Configuration for running tests with specialized settings.
    
    Adapts to test type and language/framework.
    """
    # Common settings
    verbose: bool = False
    parallel: bool = False
    max_workers: int = 4
    timeout: int = 300  # seconds
    
    # UI/E2E specific
    headless: bool = True
    screenshot_on_failure: bool = True
    screenshot_dir: str = "test-results/screenshots"
    video_on_failure: bool = False
    slow_mo: int = 0  # milliseconds to slow down operations
    
    # Browser specific (for UI tests)
    browser: str = "chromium"  # chromium, firefox, webkit
    viewport_width: int = 1280
    viewport_height: int = 720
    
    # Integration test specific
    setup_fixtures: bool = True
    teardown_after: bool = True
    database_rollback: bool = True
    
    # Performance test specific
    iterations: int = 100
    warmup_iterations: int = 10
    profile: bool = False
    
    # Retry settings
    retry_failed: bool = False
    max_retries: int = 2
    
    # Output settings
    capture_output: bool = True
    json_report: bool = True
    html_report: bool = False
    
    def to_command_args(self, language: str, framework: str, test_type: TestType) -> List[str]:
        """
        Convert config to command-line arguments for specific framework.
        
        Args:
            language: Programming language
            framework: Test framework
            test_type: Type of test
            
        Returns:
            List of command-line arguments
        """
        args = []
        
        # Framework-specific argument generation
        if framework == "pytest":
            args.extend(self._pytest_args(test_type))
        elif framework == "jest":
            args.extend(self._jest_args(test_type))
        elif framework == "junit":
            args.extend(self._junit_args(test_type))
        elif framework == "playwright":
            args.extend(self._playwright_args(test_type))
        elif framework == "testing":  # Go
            args.extend(self._go_test_args(test_type))
        elif framework == "nunit":
            args.extend(self._nunit_args(test_type))
        elif framework == "cargo":  # Rust
            args.extend(self._cargo_args(test_type))
        
        return args
    
    def _pytest_args(self, test_type: TestType) -> List[str]:
        """Generate pytest-specific arguments."""
        args = []
        
        if self.verbose:
            args.append("-v")
        
        if self.parallel and test_type == TestType.UNIT:
            args.extend(["-n", str(self.max_workers)])  # pytest-xdist
        
        if test_type in [TestType.UI, TestType.E2E]:
            # Playwright-pytest specific
            if self.headless:
                args.append("--headed=false")
            else:
                args.append("--headed")
            
            if self.screenshot_on_failure:
                args.append("--screenshot=on")
            
            args.extend(["--browser", self.browser])
        
        if self.retry_failed:
            args.extend(["--reruns", str(self.max_retries)])
        
        if self.json_report:
            args.append("--json-report")
        
        return args
    
    def _jest_args(self, test_type: TestType) -> List[str]:
        """Generate Jest-specific arguments."""
        args = []
        
        if self.verbose:
            args.append("--verbose")
        
        if self.parallel and test_type == TestType.UNIT:
            args.extend(["--maxWorkers", str(self.max_workers)])
        
        if test_type in [TestType.UI, TestType.E2E]:
            # Playwright-test specific
            args.append("--project=chromium")  # or configured browser
            
            if not self.headless:
                args.append("--headed")
            
            if self.screenshot_on_failure:
                args.append("--screenshot=only-on-failure")
        
        if self.json_report:
            args.append("--json")
        
        return args
    
    def _playwright_args(self, test_type: TestType) -> List[str]:
        """Generate Playwright-specific arguments."""
        args = []
        
        if not self.headless:
            args.append("--headed")
        
        args.extend(["--project", self.browser])
        
        if self.screenshot_on_failure:
            args.append("--screenshot=only-on-failure")
        
        if self.video_on_failure:
            args.append("--video=retain-on-failure")
        
        if self.parallel:
            args.extend(["--workers", str(self.max_workers)])
        
        return args
    
    def _junit_args(self, test_type: TestType) -> List[str]:
        """Generate JUnit/Maven/Gradle arguments."""
        args = []
        
        if self.parallel:
            args.append("-Djunit.jupiter.execution.parallel.enabled=true")
        
        return args
    
    def _go_test_args(self, test_type: TestType) -> List[str]:
        """Generate Go test arguments."""
        args = []
        
        if self.verbose:
            args.append("-v")
        
        if self.parallel:
            args.extend(["-parallel", str(self.max_workers)])
        
        if test_type == TestType.PERFORMANCE:
            args.append("-bench=.")
        
        return args
    
    def _nunit_args(self, test_type: TestType) -> List[str]:
        """Generate NUnit/dotnet test arguments."""
        args = []
        
        if self.parallel:
            args.append("--parallel")
        
        return args
    
    def _cargo_args(self, test_type: TestType) -> List[str]:
        """Generate Rust cargo test arguments."""
        args = []
        
        if self.parallel:
            args.extend(["--", "--test-threads", str(self.max_workers)])
        
        if test_type == TestType.PERFORMANCE:
            args.append("--bench")
        
        return args


class UniversalTestExecutor:
    """
    Execute tests with specialized configuration based on type and language.
    
    Automatically applies appropriate settings for:
    - UI/E2E tests (headless, screenshots, etc.)
    - Unit tests (fast, parallel)
    - Integration tests (fixtures, setup/teardown)
    - Performance tests (benchmarking, profiling)
    """
    
    def __init__(
        self,
        runner: BaseTestRunner,
        detector: Optional[UniversalTestTypeDetector] = None
    ):
        """
        Initialize executor.
        
        Args:
            runner: Test runner instance
            detector: Test type detector (optional)
        """
        self.runner = runner
        self.detector = detector or UniversalTestTypeDetector(
            runner.get_language(),
            runner.get_framework()
        )
        self.default_configs = self._create_default_configs()
    
    def _create_default_configs(self) -> Dict[TestType, TestExecutionConfig]:
        """Create default configurations for each test type."""
        return {
            TestType.UNIT: TestExecutionConfig(
                parallel=True,
                max_workers=4,
                timeout=60,
                headless=True,
                screenshot_on_failure=False
            ),
            TestType.INTEGRATION: TestExecutionConfig(
                parallel=False,  # Often needs sequential execution
                timeout=300,
                setup_fixtures=True,
                teardown_after=True,
                database_rollback=True
            ),
            TestType.UI: TestExecutionConfig(
                headless=True,
                screenshot_on_failure=True,
                video_on_failure=False,
                timeout=600,
                parallel=True,
                max_workers=2,  # Fewer workers for UI tests
                slow_mo=0
            ),
            TestType.E2E: TestExecutionConfig(
                headless=True,
                screenshot_on_failure=True,
                video_on_failure=True,
                timeout=900,
                parallel=False,  # E2E often sequential
                retry_failed=True,
                max_retries=2
            ),
            TestType.PERFORMANCE: TestExecutionConfig(
                parallel=False,  # Performance tests need isolation
                iterations=100,
                warmup_iterations=10,
                profile=True,
                timeout=1800
            ),
            TestType.API: TestExecutionConfig(
                parallel=True,
                max_workers=8,  # API tests can be highly parallel
                timeout=120,
                retry_failed=True,
                max_retries=3
            )
        }
    
    def execute_with_auto_config(
        self,
        test_file: str,
        custom_config: Optional[TestExecutionConfig] = None
    ) -> TestResults:
        """
        Execute test with auto-detected configuration.
        
        Args:
            test_file: Path to test file
            custom_config: Override default config
            
        Returns:
            TestResults from execution
        """
        # Detect test type
        classification = self.detector.classify_test_file(test_file)
        test_type = classification.primary_type
        
        # Get appropriate config
        config = custom_config or self.default_configs.get(
            test_type,
            self.default_configs[TestType.UNIT]
        )
        
        # Generate command arguments
        extra_args = config.to_command_args(
            self.runner.get_language(),
            self.runner.get_framework(),
            test_type
        )
        
        # Execute
        return self.runner.run_tests(
            str(Path(test_file).parent),
            pattern=Path(test_file).name,
            **{"extra_args": extra_args}
        )
    
    def execute_ui_tests(
        self,
        test_dir: str,
        headless: bool = True,
        screenshot: bool = True,
        browser: str = "chromium"
    ) -> TestResults:
        """
        Execute UI/E2E tests with specialized config.
        
        Args:
            test_dir: Directory containing UI tests
            headless: Run in headless mode
            screenshot: Capture screenshots on failure
            browser: Browser to use
            
        Returns:
            TestResults from execution
        """
        # Separate UI tests from others
        _, ui_tests = self.detector.separate_unit_and_ui_tests(test_dir)
        
        if not ui_tests:
            return TestResults(
                total=0,
                language=self.runner.get_language(),
                framework=self.runner.get_framework()
            )
        
        # Create UI-specific config
        config = TestExecutionConfig(
            headless=headless,
            screenshot_on_failure=screenshot,
            browser=browser,
            timeout=600,
            parallel=True,
            max_workers=2
        )
        
        # Run UI tests
        all_results = []
        for ui_test in ui_tests:
            results = self.execute_with_auto_config(str(ui_test), config)
            all_results.append(results)
        
        # Aggregate results
        return self._aggregate_results(all_results)
    
    def execute_unit_tests_fast(self, test_dir: str) -> TestResults:
        """
        Execute unit tests with maximum parallelization.
        
        Args:
            test_dir: Directory containing tests
            
        Returns:
            TestResults from execution
        """
        # Separate unit tests
        unit_tests, _ = self.detector.separate_unit_and_ui_tests(test_dir)
        
        if not unit_tests:
            return TestResults(
                total=0,
                language=self.runner.get_language(),
                framework=self.runner.get_framework()
            )
        
        # Fast unit test config
        config = TestExecutionConfig(
            parallel=True,
            max_workers=8,  # Max parallelization
            timeout=30,
            headless=True
        )
        
        return self.runner.run_tests(test_dir, **{
            "extra_args": config.to_command_args(
                self.runner.get_language(),
                self.runner.get_framework(),
                TestType.UNIT
            )
        })
    
    def execute_all_with_optimization(self, test_dir: str) -> Dict[TestType, TestResults]:
        """
        Execute all tests with optimized configuration per type.
        
        Args:
            test_dir: Directory containing all tests
            
        Returns:
            Dictionary mapping test types to results
        """
        # Classify all tests
        classifications = self.detector.classify_directory(test_dir)
        
        results_by_type = {}
        
        # Execute each type with appropriate config
        for test_type, test_files in classifications.items():
            if not test_files or test_type == TestType.UNKNOWN:
                continue
            
            config = self.default_configs.get(test_type)
            type_results = []
            
            for test_file in test_files:
                result = self.execute_with_auto_config(str(test_file), config)
                type_results.append(result)
            
            results_by_type[test_type] = self._aggregate_results(type_results)
        
        return results_by_type
    
    def _aggregate_results(self, results: List[TestResults]) -> TestResults:
        """Aggregate multiple test results into one."""
        if not results:
            return TestResults(
                total=0,
                language=self.runner.get_language(),
                framework=self.runner.get_framework()
            )
        
        aggregated = TestResults(
            language=self.runner.get_language(),
            framework=self.runner.get_framework()
        )
        
        for result in results:
            aggregated.total += result.total
            aggregated.passed += result.passed
            aggregated.failed += result.failed
            aggregated.skipped += result.skipped
            aggregated.errors += result.errors
            aggregated.duration += result.duration
        
        return aggregated

"""
Universal Test Type Detector for TestGen AI.

Detects and classifies test types across ALL 14 languages:
- Unit tests
- Integration tests  
- UI/E2E tests
- Performance tests
- etc.
"""

from pathlib import Path
from typing import List, Set, Optional, Dict
from enum import Enum
from dataclasses import dataclass


class TestType(Enum):
    """Types of tests we can detect across all languages."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"  # End-to-end
    UI = "ui"  # UI/Browser tests
    PERFORMANCE = "performance"
    API = "api"
    DATABASE = "database"
    SMOKE = "smoke"
    ACCEPTANCE = "acceptance"
    UNKNOWN = "unknown"


@dataclass
class TestFileClassification:
    """Classification result for a test file."""
    file_path: Path
    language: str
    framework: str
    test_types: Set[TestType]
    primary_type: TestType
    confidence: float  # 0.0 to 1.0
    detection_signals: List[str]  # What triggered the detection
    
    @property
    def is_unit_test(self) -> bool:
        return TestType.UNIT in self.test_types
    
    @property
    def is_integration_test(self) -> bool:
        return TestType.INTEGRATION in self.test_types
    
    @property
    def is_ui_test(self) -> bool:
        return TestType.UI in self.test_types or TestType.E2E in self.test_types
    
    @property
    def is_performance_test(self) -> bool:
        return TestType.PERFORMANCE in self.test_types


class UniversalTestTypeDetector:
    """
    Detect test types across ALL 14 programming languages.
    
    Identifies unit tests, integration tests, UI tests, etc.
    Works with language-specific patterns and conventions.
    """
    
    # UI/E2E testing libraries by language
    UI_TESTING_PATTERNS = {
        # JavaScript/TypeScript
        "javascript": {
            "imports": ["playwright", "puppeteer", "cypress", "selenium", "webdriver", "testcafe"],
            "functions": ["page.", "browser.", "cy.", "element(", "driver."],
            "keywords": ["screenshot", "navigate", "click", "type", "waitFor"]
        },
        "typescript": {
            "imports": ["playwright", "puppeteer", "cypress", "selenium", "webdriver", "testcafe"],
            "functions": ["page.", "browser.", "cy.", "element(", "driver."],
            "keywords": ["screenshot", "navigate", "click", "type", "waitFor"]
        },
        
        # Python
        "python": {
            "imports": ["playwright", "selenium", "pyppeteer", "splinter", "mechanize"],
            "functions": ["page.", "driver.", "browser."],
            "keywords": ["screenshot", "navigate", "click", "send_keys", "wait"]
        },
        
        # Java
        "java": {
            "imports": ["org.openqa.selenium", "io.github.bonigarcia", "org.testcontainers"],
            "functions": ["WebDriver", "findElement", "ChromeDriver"],
            "keywords": ["click()", "sendKeys", "navigate"]
        },
        
        # C#
        "csharp": {
            "imports": ["Selenium", "Playwright", "Puppeteer"],
            "functions": ["IWebDriver", "FindElement"],
            "keywords": ["Click()", "SendKeys"]
        },
        
        # Ruby
        "ruby": {
            "imports": ["capybara", "selenium", "watir"],
            "functions": ["visit", "click_button", "fill_in"],
            "keywords": ["screenshot", "page."]
        },
        
        # Go
        "go": {
            "imports": ["chromedp", "selenium"],
            "functions": ["chromedp.", "Navigate"],
            "keywords": ["Click", "SendKeys"]
        },
        
        # PHP
        "php": {
            "imports": ["Facebook\\WebDriver", "Behat", "Codeception"],
            "functions": ["$driver->", "$browser->"],
            "keywords": ["click()", "sendKeys"]
        }
    }
    
    # Integration test patterns
    INTEGRATION_PATTERNS = {
        "imports": ["requests", "http", "api", "rest", "graphql", "grpc"],
        "keywords": ["mock", "stub", "fixture", "setup", "teardown", "database", "db", "sql"],
        "decorators": ["@integration", "@database", "@api"],
        "names": ["integration", "e2e", "integration_test", "api_test"]
    }
    
    # Performance test patterns
    PERFORMANCE_PATTERNS = {
        "imports": ["pytest-benchmark", "locust", "jmeter", "k6", "gatling", "benchmark"],
        "keywords": ["benchmark", "load", "stress", "performance"],
        "decorators": ["@benchmark", "@performance", "@load"]
    }
    
    def __init__(self, language: str, framework: str):
        """
        Initialize detector for specific language.
        
        Args:
            language: Programming language
            framework: Test framework
        """
        self.language = language.lower()
        self.framework = framework.lower()
    
    def classify_test_file(self, file_path: str) -> TestFileClassification:
        """
        Classify a test file and determine its type(s).
        
        Args:
            file_path: Path to test file
            
        Returns:
            TestFileClassification with detected types
        """
        path = Path(file_path)
        
        if not path.exists():
            return TestFileClassification(
                file_path=path,
                language=self.language,
                framework=self.framework,
                test_types={TestType.UNKNOWN},
                primary_type=TestType.UNKNOWN,
                confidence=0.0,
                detection_signals=["File not found"]
            )
        
        try:
            content = path.read_text(encoding='utf-8')
        except:
            return TestFileClassification(
                file_path=path,
                language=self.language,
                framework=self.framework,
                test_types={TestType.UNKNOWN},
                primary_type=TestType.UNKNOWN,
                confidence=0.0,
                detection_signals=["Cannot read file"]
            )
        
        # Detect all test types
        detected_types = set()
        signals = []
        confidence_scores = {}
        
        # Check for UI/E2E tests
        ui_score, ui_signals = self._detect_ui_test(content, path)
        if ui_score > 0.3:
            detected_types.add(TestType.UI)
            signals.extend(ui_signals)
            confidence_scores[TestType.UI] = ui_score
        
        # Check for integration tests
        int_score, int_signals = self._detect_integration_test(content, path)
        if int_score > 0.3:
            detected_types.add(TestType.INTEGRATION)
            signals.extend(int_signals)
            confidence_scores[TestType.INTEGRATION] = int_score
        
        # Check for performance tests
        perf_score, perf_signals = self._detect_performance_test(content, path)
        if perf_score > 0.3:
            detected_types.add(TestType.PERFORMANCE)
            signals.extend(perf_signals)
            confidence_scores[TestType.PERFORMANCE] = perf_score
        
        # Check for API tests
        api_score, api_signals = self._detect_api_test(content, path)
        if api_score > 0.3:
            detected_types.add(TestType.API)
            signals.extend(api_signals)
            confidence_scores[TestType.API] = api_score
        
        # Default to unit test if no specific type detected
        if not detected_types:
            detected_types.add(TestType.UNIT)
            signals.append("Default: No specific test type markers found")
            confidence_scores[TestType.UNIT] = 0.5
        
        # Determine primary type (highest confidence)
        primary_type = max(confidence_scores.keys(), key=lambda k: confidence_scores[k])
        confidence = confidence_scores[primary_type]
        
        return TestFileClassification(
            file_path=path,
            language=self.language,
            framework=self.framework,
            test_types=detected_types,
            primary_type=primary_type,
            confidence=confidence,
            detection_signals=signals
        )
    
    def _detect_ui_test(self, content: str, path: Path) -> tuple[float, List[str]]:
        """Detect UI/E2E tests."""
        score = 0.0
        signals = []
        
        # Check file name
        name_lower = path.stem.lower()
        if any(keyword in name_lower for keyword in ["ui", "e2e", "browser", "selenium", "playwright"]):
            score += 0.3
            signals.append(f"Filename contains UI keywords: {path.stem}")
        
        # Get language-specific patterns
        patterns = self.UI_TESTING_PATTERNS.get(self.language, {})
        
        # Check imports
        for import_pattern in patterns.get("imports", []):
            if import_pattern.lower() in content.lower():
                score += 0.4
                signals.append(f"Imports UI library: {import_pattern}")
        
        # Check function calls
        for func_pattern in patterns.get("functions", []):
            if func_pattern in content:
                score += 0.2
                signals.append(f"Uses UI function: {func_pattern}")
        
        # Check keywords
        for keyword in patterns.get("keywords", []):
            if keyword.lower() in content.lower():
                score += 0.1
                signals.append(f"Uses UI keyword: {keyword}")
        
        return min(score, 1.0), signals
    
    def _detect_integration_test(self, content: str, path: Path) -> tuple[float, List[str]]:
        """Detect integration tests."""
        score = 0.0
        signals = []
        
        # Check file name
        name_lower = path.stem.lower()
        if any(keyword in name_lower for keyword in ["integration", "int_test", "e2e"]):
            score += 0.4
            signals.append(f"Filename suggests integration: {path.stem}")
        
        # Check for integration keywords
        for keyword in self.INTEGRATION_PATTERNS["keywords"]:
            if keyword in content.lower():
                score += 0.1
                signals.append(f"Contains integration keyword: {keyword}")
        
        # Check for database/API imports
        for import_pattern in self.INTEGRATION_PATTERNS["imports"]:
            if import_pattern in content.lower():
                score += 0.2
                signals.append(f"Imports integration library: {import_pattern}")
        
        return min(score, 1.0), signals
    
    def _detect_performance_test(self, content: str, path: Path) -> tuple[float, List[str]]:
        """Detect performance/benchmark tests."""
        score = 0.0
        signals = []
        
        # Check file name
        name_lower = path.stem.lower()
        if any(keyword in name_lower for keyword in ["perf", "bench", "load", "stress"]):
            score += 0.5
            signals.append(f"Filename suggests performance test: {path.stem}")
        
        # Check for performance keywords
        for keyword in self.PERFORMANCE_PATTERNS["keywords"]:
            if keyword in content.lower():
                score += 0.2
                signals.append(f"Contains performance keyword: {keyword}")
        
        # Check for performance imports
        for import_pattern in self.PERFORMANCE_PATTERNS["imports"]:
            if import_pattern in content.lower():
                score += 0.3
                signals.append(f"Imports performance library: {import_pattern}")
        
        return min(score, 1.0), signals
    
    def _detect_api_test(self, content: str, path: Path) -> tuple[float, List[str]]:
        """Detect API tests."""
        score = 0.0
        signals = []
        
        # Check file name
        name_lower = path.stem.lower()
        if any(keyword in name_lower for keyword in ["api", "rest", "graphql", "endpoint"]):
            score += 0.4
            signals.append(f"Filename suggests API test: {path.stem}")
        
        # Check for API-specific keywords
        api_keywords = ["requests.", "http.", "get(", "post(", "put(", "delete(", "patch(", "endpoint", "baseurl"]
        for keyword in api_keywords:
            if keyword.lower() in content.lower():
                score += 0.15
                signals.append(f"Contains API keyword: {keyword}")
        
        return min(score, 1.0), signals
    
    def classify_directory(self, test_dir: str, pattern: str = "**/*test*") -> Dict[TestType, List[Path]]:
        """
        Classify all test files in a directory.
        
        Args:
            test_dir: Directory containing tests
            pattern: Glob pattern for test files
            
        Returns:
            Dictionary mapping test types to file lists
        """
        test_path = Path(test_dir)
        if not test_path.exists():
            return {}
        
        results = {test_type: [] for test_type in TestType}
        
        for test_file in test_path.glob(pattern):
            if test_file.is_file():
                classification = self.classify_test_file(str(test_file))
                results[classification.primary_type].append(test_file)
        
        return results
    
    def separate_unit_and_ui_tests(self, test_dir: str) -> tuple[List[Path], List[Path]]:
        """
        Separate unit tests from UI tests.
        
        Args:
            test_dir: Directory containing tests
            
        Returns:
            Tuple of (unit_tests, ui_tests)
        """
        classifications = self.classify_directory(test_dir)
        
        unit_tests = classifications.get(TestType.UNIT, [])
        ui_tests = (
            classifications.get(TestType.UI, []) + 
            classifications.get(TestType.E2E, [])
        )
        
        return unit_tests, ui_tests
    
    def get_test_summary(self, test_dir: str) -> Dict[str, int]:
        """
        Get summary of test types in directory.
        
        Args:
            test_dir: Directory containing tests
            
        Returns:
            Dictionary with counts per test type
        """
        classifications = self.classify_directory(test_dir)
        
        return {
            test_type.value: len(files)
            for test_type, files in classifications.items()
            if len(files) > 0
        }

"""
Language Detection for TestGen AI.

Detects programming language and test framework from project structure.
"""

from pathlib import Path
from typing import Optional, List
from enum import Enum


class Language(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    CSHARP = "csharp"
    RUBY = "ruby"
    UNKNOWN = "unknown"


class TestFramework(Enum):
    """Supported test frameworks."""
    # Python
    PYTEST = "pytest"
    UNITTEST = "unittest"
    
    # JavaScript/TypeScript
    JEST = "jest"
    MOCHA = "mocha"
    VITEST = "vitest"
    JASMINE = "jasmine"
    
    # Java
    JUNIT = "junit"
    TESTNG = "testng"
    
    # Go
    GO_TEST = "go_test"
    
    # C#
    NUNIT = "nunit"
    XUNIT = "xunit"
    MSTEST = "mstest"
    
    # Ruby
    RSPEC = "rspec"
    MINITEST = "minitest"
    
    UNKNOWN = "unknown"


class LanguageDetector:
    """
    Detects programming language and test framework.
    
    Example:
        >>> detector = LanguageDetector()
        >>> lang = detector.detect_language("./my-project")
        >>> framework = detector.detect_test_framework("./my-project")
    """
    
    # Language indicators (filename -> language)
    LANGUAGE_FILES = {
        "package.json": Language.JAVASCRIPT,
        "tsconfig.json": Language.TYPESCRIPT,
        "requirements.txt": Language.PYTHON,
        "pyproject.toml": Language.PYTHON,
        "setup.py": Language.PYTHON,
        "Pipfile": Language.PYTHON,
        "pom.xml": Language.JAVA,
        "build.gradle": Language.JAVA,
        "build.gradle.kts": Language.JAVA,
        "go.mod": Language.GO,
        "Gemfile": Language.RUBY,
        "*.csproj": Language.CSHARP,
        "*.sln": Language.CSHARP,
    }
    
    def detect_language(self, project_dir: str) -> Language:
        """
        Detect programming language from project structure.
        
        Args:
            project_dir: Project directory path
            
        Returns:
            Detected Language
        """
        path = Path(project_dir)
        
        if not path.exists():
            return Language.UNKNOWN
        
        # Check for language indicator files
        for filename, language in self.LANGUAGE_FILES.items():
            if "*" in filename:
                # Pattern matching (e.g., *.csproj)
                pattern = filename.replace("*", "")
                if list(path.rglob(f"*{pattern}")):
                    return language
            else:
                # Direct file check
                if (path / filename).exists():
                    return language
        
        # Check by file extensions
        file_counts = self._count_file_extensions(path)
        
        if file_counts.get(".py", 0) > 0:
            return Language.PYTHON
        elif file_counts.get(".js", 0) > 0:
            return Language.JAVASCRIPT
        elif file_counts.get(".ts", 0) > 0:
            return Language.TYPESCRIPT
        elif file_counts.get(".java", 0) > 0:
            return Language.JAVA
        elif file_counts.get(".go", 0) > 0:
            return Language.GO
        elif file_counts.get(".cs", 0) > 0:
            return Language.CSHARP
        elif file_counts.get(".rb", 0) > 0:
            return Language.RUBY
        
        return Language.UNKNOWN
    
    def detect_test_framework(
        self,
        project_dir: str,
        language: Optional[Language] = None
    ) -> TestFramework:
        """
        Detect test framework.
        
        Args:
            project_dir: Project directory
            language: Known language (optional, will auto-detect)
            
        Returns:
            Detected TestFramework
        """
        if language is None:
            language = self.detect_language(project_dir)
        
        path = Path(project_dir)
        
        if language == Language.PYTHON:
            return self._detect_python_framework(path)
        elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            return self._detect_javascript_framework(path)
        elif language == Language.JAVA:
            return self._detect_java_framework(path)
        elif language == Language.GO:
            return TestFramework.GO_TEST
        elif language == Language.CSHARP:
            return self._detect_csharp_framework(path)
        elif language == Language.RUBY:
            return self._detect_ruby_framework(path)
        
        return TestFramework.UNKNOWN
    
    def _detect_python_framework(self, path: Path) -> TestFramework:
        """Detect Python test framework."""
        # Check for pytest
        if (path / "pytest.ini").exists() or (path / "pyproject.toml").exists():
            # Check pyproject.toml for pytest
            pyproject = path / "pyproject.toml"
            if pyproject.exists():
                content = pyproject.read_text()
                if "pytest" in content:
                    return TestFramework.PYTEST
        
        # Check for pytest in requirements
        req_files = ["requirements.txt", "requirements-dev.txt", "dev-requirements.txt"]
        for req_file in req_files:
            req_path = path / req_file
            if req_path.exists():
                content = req_path.read_text()
                if "pytest" in content:
                    return TestFramework.PYTEST
        
        # Check test files for pytest imports
        test_files = list(path.rglob("test_*.py"))
        for test_file in test_files[:5]:  # Check first 5 files
            try:
                content = test_file.read_text()
                if "import pytest" in content or "from pytest" in content:
                    return TestFramework.PYTEST
                elif "import unittest" in content:
                    return TestFramework.UNITTEST
            except:
                pass
        
        # Default to pytest for Python
        return TestFramework.PYTEST
    
    def _detect_javascript_framework(self, path: Path) -> TestFramework:
        """Detect JavaScript/TypeScript test framework."""
        package_json = path / "package.json"
        
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                # Check dependencies
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                if "jest" in deps:
                    return TestFramework.JEST
                elif "vitest" in deps:
                    return TestFramework.VITEST
                elif "mocha" in deps:
                    return TestFramework.MOCHA
                elif "jasmine" in deps:
                    return TestFramework.JASMINE
            except:
                pass
        
        # Check for config files
        if (path / "jest.config.js").exists() or (path / "jest.config.ts").exists():
            return TestFramework.JEST
        elif (path / "vitest.config.js").exists() or (path / "vitest.config.ts").exists():
            return TestFramework.VITEST
        
        # Default to Jest for JS/TS
        return TestFramework.JEST
    
    def _detect_java_framework(self, path: Path) -> TestFramework:
        """Detect Java test framework."""
        # Check pom.xml
        pom = path / "pom.xml"
        if pom.exists():
            content = pom.read_text()
            if "junit-jupiter" in content or "junit5" in content:
                return TestFramework.JUNIT
            elif "testng" in content:
                return TestFramework.TESTNG
        
        # Check build.gradle
        gradle_files = list(path.glob("build.gradle*"))
        for gradle in gradle_files:
            content = gradle.read_text()
            if "junit" in content.lower():
                return TestFramework.JUNIT
            elif "testng" in content.lower():
                return TestFramework.TESTNG
        
        return TestFramework.JUNIT
    
    def _detect_csharp_framework(self, path: Path) -> TestFramework:
        """Detect C# test framework."""
        # Check .csproj files
        csproj_files = list(path.rglob("*.csproj"))
        for csproj in csproj_files:
            content = csproj.read_text()
            if "nunit" in content.lower():
                return TestFramework.NUNIT
            elif "xunit" in content.lower():
                return TestFramework.XUNIT
            elif "mstest" in content.lower():
                return TestFramework.MSTEST
        
        return TestFramework.NUNIT
    
    def _detect_ruby_framework(self, path: Path) -> TestFramework:
        """Detect Ruby test framework."""
        gemfile = path / "Gemfile"
        if gemfile.exists():
            content = gemfile.read_text()
            if "rspec" in content:
                return TestFramework.RSPEC
            elif "minitest" in content:
                return TestFramework.MINITEST
        
        return TestFramework.RSPEC
    
    def _count_file_extensions(self, path: Path) -> dict:
        """Count files by extension."""
        counts = {}
        
        # Only check source directories
        source_dirs = ["src", "lib", "app", ""]
        
        for source_dir in source_dirs:
            search_path = path / source_dir if source_dir else path
            if not search_path.exists():
                continue
            
            for file in search_path.rglob("*"):
                if file.is_file() and not any(p in str(file) for p in ["node_modules", "__pycache__", ".git", "vendor"]):
                    ext = file.suffix
                    if ext:
                        counts[ext] = counts.get(ext, 0) + 1
        
        return counts
    
    def get_project_info(self, project_dir: str) -> dict:
        """
        Get complete project information.
        
        Returns:
            Dictionary with language, framework, and other info
        """
        language = self.detect_language(project_dir)
        framework = self.detect_test_framework(project_dir, language)
        
        return {
            "language": language.value,
            "test_framework": framework.value,
            "project_dir": project_dir,
            "is_multi_language": self._check_multi_language(project_dir)
        }
    
    def _check_multi_language(self, project_dir: str) -> bool:
        """Check if project uses multiple languages."""
        path = Path(project_dir)
        extensions = self._count_file_extensions(path)
        
        # Count significant languages
        lang_indicators = {
            ".py": Language.PYTHON,
            ".js": Language.JAVASCRIPT,
            ".ts": Language.TYPESCRIPT,
            ".java": Language.JAVA,
            ".go": Language.GO,
            ".cs": Language.CSHARP,
            ".rb": Language.RUBY,
        }
        
        languages_found = set()
        for ext, count in extensions.items():
            if ext in lang_indicators and count > 5:  # At least 5 files
                languages_found.add(lang_indicators[ext])
        
        return len(languages_found) > 1

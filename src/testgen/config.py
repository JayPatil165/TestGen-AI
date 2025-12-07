"""
Configuration management for TestGen AI.

This module handles all configuration settings including API keys,
model selection, and project-specific settings.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class TestFramework(str, Enum):
    """Supported test frameworks."""
    
    PYTEST = "pytest"
    UNITTEST = "unittest"


class Config(BaseSettings):
    """
    Main configuration class for TestGen AI.
    
    All settings can be configured via:
    1. Environment variables (highest priority)
    2. .env file
    3. Default values (lowest priority)
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ===== LLM Configuration =====
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for GPT models"
    )
    
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude models"
    )
    
    llm_provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM provider to use (openai, anthropic, ollama)"
    )
    
    llm_model: str = Field(
        default="gpt-4",
        description="Specific model to use (e.g., gpt-4, gpt-3.5-turbo, claude-3, ollama/codellama)"
    )
    
    max_context_tokens: int = Field(
        default=8000,
        description="Maximum tokens to send to LLM",
        ge=1000,
        le=100000
    )
    
    llm_temperature: float = Field(
        default=0.2,
        description="LLM temperature for generation (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    
    # ===== Test Generation Settings =====
    test_framework: TestFramework = Field(
        default=TestFramework.PYTEST,
        description="Test framework to use"
    )
    
    test_output_dir: Path = Field(
        default=Path("tests"),
        description="Directory to output generated tests"
    )
    
    test_file_prefix: str = Field(
        default="test_",
        description="Prefix for generated test files"
    )
    
    min_coverage_target: int = Field(
        default=80,
        description="Minimum coverage target percentage",
        ge=0,
        le=100
    )
    
    # ===== Scanner Settings =====
    ignore_patterns: list[str] = Field(
        default_factory=lambda: [
            "node_modules/",
            ".git/",
            "__pycache__/",
            ".venv/",
            "venv/",
            ".pytest_cache/",
            "*.pyc",
            ".coverage",
        ],
        description="Patterns to ignore when scanning code"
    )
    
    max_file_size_lines: int = Field(
        default=500,
        description="Max lines before switching to signature extraction only",
        ge=100
    )
    
    supported_extensions: list[str] = Field(
        default_factory=lambda: [".py", ".js", ".ts", ".java"],
        description="File extensions to scan"
    )
    
    # ===== Watch Mode Settings =====
    watch_debounce_seconds: float = Field(
        default=2.0,
        description="Seconds to wait before processing file changes",
        ge=0.1,
        le=10.0
    )
    
    watch_auto_run: bool = Field(
        default=False,
        description="Automatically run tests after generation in watch mode"
    )
    
    # ===== Report Settings =====
    report_output_dir: Path = Field(
        default=Path("reports"),
        description="Directory for test reports"
    )
    
    report_format: str = Field(
        default="html",
        description="Default report format (html, pdf)"
    )
    
    # ===== Execution Settings =====
    pytest_args: list[str] = Field(
        default_factory=lambda: ["--verbose", "--tb=short"],
        description="Default pytest arguments"
    )
    
    playwright_headed: bool = Field(
        default=False,
        description="Run Playwright tests in headed mode"
    )
    
    # ===== Cache Settings =====
    cache_dir: Path = Field(
        default=Path(".testgen-cache"),
        description="Directory for caching scan results and LLM responses"
    )
    
    enable_cache: bool = Field(
        default=True,
        description="Enable caching to reduce costs"
    )
    
    # ===== Logging Settings =====
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    log_file: Optional[Path] = Field(
        default=Path(".testgen/logs/testgen.log"),
        description="Log file path"
    )
    
    verbose: bool = Field(
        default=False,
        description="Enable verbose output"
    )
    
    def validate_api_keys(self) -> None:
        """Validate that required API keys are set based on provider."""
        if self.llm_provider == LLMProvider.OPENAI and not self.openai_api_key:
            raise ValueError(
                "OpenAI API key is required when using OpenAI provider. "
                "Set OPENAI_API_KEY environment variable."
            )
        
        if self.llm_provider == LLMProvider.ANTHROPIC and not self.anthropic_api_key:
            raise ValueError(
                "Anthropic API key is required when using Anthropic provider. "
                "Set ANTHROPIC_API_KEY environment variable."
            )
    
    def get_api_key(self) -> Optional[str]:
        """Get the appropriate API key based on the selected provider."""
        if self.llm_provider == LLMProvider.OPENAI:
            return self.openai_api_key
        elif self.llm_provider == LLMProvider.ANTHROPIC:
            return self.anthropic_api_key
        else:  # Ollama doesn't need an API key
            return None
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        self.report_output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = Config()

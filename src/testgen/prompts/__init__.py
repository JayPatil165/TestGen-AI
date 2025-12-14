"""
Prompt Template Management for TestGen AI.

This module provides utilities for loading and formatting prompt templates
used in test generation.
"""

from pathlib import Path
from typing import Dict, Optional


# Directory containing prompt templates
PROMPTS_DIR = Path(__file__).parent


def load_template(template_name: str) -> str:
    """
    Load a prompt template from the prompts directory.
    
    Args:
        template_name: Name of the template file (e.g., "test_generation.txt")
        
    Returns:
        Template content as a string
        
    Raises:
        FileNotFoundError: If template doesn't exist
    """
    template_path = PROMPTS_DIR / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template '{template_name}' not found in {PROMPTS_DIR}"
        )
    
    return template_path.read_text(encoding="utf-8")


def format_template(template: str, **kwargs) -> str:
    """
    Format a template with the provided variables.
    
    Args:
        template: Template string with placeholders
        **kwargs: Variables to substitute in template
        
    Returns:
        Formatted template string
        
    Example:
        >>> template = load_template("test_generation.txt")
        >>> prompt = format_template(template, code_context="def add(a, b): return a + b")
    """
    return template.format(**kwargs)


def get_system_instruction() -> str:
    """
    Get the standard system instruction for test generation.
    
    Returns:
        System instruction content
    """
    return load_template("system_instruction.txt")


def get_test_generation_prompt(
    code_context: str,
    file_path: Optional[str] = None,
    framework: str = "pytest",
    coverage_target: int = 80,
    include_examples: bool = False
) -> str:
    """
    Get a complete test generation prompt with all context.
    
    Args:
        code_context: The code to generate tests for
        file_path: Optional path to the file being tested
        framework: Test framework to use (default: pytest)
        coverage_target: Target coverage percentage (default: 80)
        include_examples: Whether to include few-shot examples (default: False)
        
    Returns:
        Complete formatted prompt ready for LLM
        
    Example:
        >>> code = "def multiply(x, y): return x * y"
        >>> prompt = get_test_generation_prompt(
        ...     code_context=code,
        ...     file_path="utils/math.py"
        ... )
    """
    # Load main template
    template = load_template("test_generation.txt")
    
    # Format with provided context
    prompt = format_template(
        template,
        code_context=code_context
    )
    
    # Optionally include few-shot examples
    if include_examples:
        examples = load_template("few_shot_examples.txt")
        prompt = f"{examples}\n\n{prompt}"
    
    # Add file path context if provided
    if file_path:
        prompt = f"## File: {file_path}\n\n{prompt}"
    
    return prompt


def list_templates() -> list[str]:
    """
    List all available prompt templates.
    
    Returns:
        List of template filenames
    """
    return [
        f.name
        for f in PROMPTS_DIR.glob("*.txt")
        if f.is_file()
    ]


class PromptBuilder:
    """
    Builder class for constructing prompts with various options.
    
    Example:
        >>> builder = PromptBuilder(code_context="def foo(): pass")
        >>> builder.with_file_path("src/main.py")
        >>> builder.with_examples()
        >>> prompt = builder.build()
    """
    
    def __init__(self, code_context: str):
        """
        Initialize prompt builder.
        
        Args:
            code_context: The code to generate tests for
        """
        self.code_context = code_context
        self._file_path: Optional[str] = None
        self._framework: str = "pytest"
        self._coverage_target: int = 80
        self._include_examples: bool = False
        self._custom_instructions: list[str] = []
    
    def with_file_path(self, file_path: str) -> "PromptBuilder":
        """Add file path context."""
        self._file_path = file_path
        return self
    
    def with_framework(self, framework: str) -> "PromptBuilder":
        """Specify test framework."""
        self._framework = framework
        return self
    
    def with_coverage_target(self, target: int) -> "PromptBuilder":
        """Set coverage target percentage."""
        self._coverage_target = target
        return self
    
    def with_examples(self) -> "PromptBuilder":
        """Include few-shot examples in prompt."""
        self._include_examples = True
        return self
    
    def with_custom_instruction(self, instruction: str) -> "PromptBuilder":
        """Add custom instruction to the prompt."""
        self._custom_instructions.append(instruction)
        return self
    
    def build(self) -> str:
        """
        Build the final prompt.
        
        Returns:
            Complete formatted prompt
        """
        prompt = get_test_generation_prompt(
            code_context=self.code_context,
            file_path=self._file_path,
            framework=self._framework,
            coverage_target=self._coverage_target,
            include_examples=self._include_examples
        )
        
        # Add custom instructions if any
        if self._custom_instructions:
            custom = "\n".join(f"- {inst}" for inst in self._custom_instructions)
            prompt = f"{prompt}\n\n## Additional Instructions:\n{custom}"
        
        return prompt


# Convenience functions
def create_test_prompt(code: str, **options) -> str:
    """
    Convenience function to create a test generation prompt.
    
    Args:
        code: Code to generate tests for
        **options: Additional options (file_path, framework, etc.)
        
    Returns:
        Formatted prompt
    """
    return get_test_generation_prompt(code_context=code, **options)

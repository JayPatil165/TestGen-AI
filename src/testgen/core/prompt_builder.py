"""
Enhanced Prompt Builder for TestGen AI.

This module provides advanced prompt building capabilities with
framework-specific instructions and batch processing.
"""

from typing import Optional, List, Dict
from pathlib import Path

from testgen.core.scanner import ScanResult, CodeFile
from testgen.core.prompt_generator import TestPromptGenerator, create_prompt_for_scan_result


class AdvancedPromptBuilder:
    """
    Advanced prompt builder with framework-specific instructions.
    
    Builds comprehensive prompts from scan results with support for:
    - pytest and unittest frameworks
    - Custom instructions
    - Batch processing
    - Context optimization
    
    Example:
        >>> builder = AdvancedPromptBuilder(framework="pytest")
        >>> prompts = builder.build_from_scan_result(scan_result)
        >>> for file, system, user in prompts:
        ...     # Send to LLM
        ...     pass
    """
    
    def __init__(
        self,
        framework: str = "pytest",
        coverage_target: int = 80,
        include_examples: bool = False,
        max_files: Optional[int] = None
    ):
        """
        Initialize advanced prompt builder.
        
        Args:
            framework: Test framework (pytest or unittest)
            coverage_target: Target coverage percentage
            include_examples: Include few-shot examples
            max_files: Maximum files to process (None = all)
        """
        self.framework = framework
        self.coverage_target = coverage_target
        self.include_examples = include_examples
        self.max_files = max_files
        self.generator = TestPromptGenerator(
            include_examples=include_examples,
            coverage_target=coverage_target,
            framework=framework
        )
    
    def build_prompt(self, scan_result: ScanResult) -> List[Dict[str, str]]:
        """
        Build prompts from scan result (Task 37 requirement).
        
        Args:
            scan_result: ScanResult from code scanner
            
        Returns:
            List of prompt dictionaries with keys:
            - file_path: Path to file
            - system_prompt: System instruction
            - user_prompt: User prompt with code context
            - framework: Test framework
            - metadata: Additional metadata
            
        Example:
            >>> builder = AdvancedPromptBuilder()
            >>> prompts = builder.build_prompt(scan_result)
            >>> for prompt_data in prompts:
            ...     llm.generate(
            ...         system_prompt=prompt_data["system_prompt"],
            ...         prompt=prompt_data["user_prompt"]
            ...     )
        """
        prompts = []
        
        # Get system prompt (same for all files)
        system_prompt = self.generator.get_system_prompt()
        
        # Add framework-specific instructions
        framework_instructions = self._get_framework_instructions()
        if framework_instructions:
            system_prompt = f"{system_prompt}\n\n{framework_instructions}"
        
        # Process files
        files_to_process = scan_result.files
        if self.max_files:
            files_to_process = files_to_process[:self.max_files]
        
        for code_file in files_to_process:
            # Skip if no content
            if not code_file.content and not (code_file.functions or code_file.classes):
                continue
            
            try:
                # Generate user prompt
                user_prompt = self.generator.generate_for_file(code_file)
                
                # Insert code context
                user_prompt = self._insert_code_context(user_prompt, code_file)
                
                # Build prompt dict
                prompt_data = {
                    "file_path": str(code_file.relative_path),
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "framework": self.framework,
                    "metadata": {
                        "line_count": code_file.line_count,
                        "functions": len(code_file.functions),
                        "classes": len(code_file.classes),
                        "file_type": code_file.file_type.value,
                        "coverage_target": self.coverage_target
                    }
                }
                
                prompts.append(prompt_data)
                
            except Exception as e:
                print(f"Warning: Failed to build prompt for {code_file.path}: {e}")
        
        return prompts
    
    def build_from_scan_result(
        self,
        scan_result: ScanResult,
        file_filter: Optional[str] = None
    ) -> List[tuple[str, str, str]]:
        """
        Build prompts from scan result (simplified tuple format).
        
        Args:
            scan_result: ScanResult from scanner
            file_filter: Optional glob pattern to filter files
            
        Returns:
            List of (file_path, system_prompt, user_prompt) tuples
        """
        prompt_dicts = self.build_prompt(scan_result)
        
        # Apply filter if specified
        if file_filter:
            prompt_dicts = [
                p for p in prompt_dicts
                if Path(p["file_path"]).match(file_filter)
            ]
        
        # Convert to simple tuple format
        return [
            (p["file_path"], p["system_prompt"], p["user_prompt"])
            for p in prompt_dicts
        ]
    
    def build_for_file(
        self,
        code_file: CodeFile,
        custom_instructions: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Build prompt for a single file with optional custom instructions.
        
        Args:
            code_file: CodeFile to generate prompt for
            custom_instructions: Optional list of additional instructions
            
        Returns:
            Prompt dictionary
        """
        system_prompt = self.generator.get_system_prompt()
        framework_instructions = self._get_framework_instructions()
        
        if framework_instructions:
            system_prompt = f"{system_prompt}\n\n{framework_instructions}"
        
        user_prompt = self.generator.generate_for_file(code_file)
        user_prompt = self._insert_code_context(user_prompt, code_file)
        
        # Add custom instructions
        if custom_instructions:
            custom_section = "\n\n## Additional Instructions:\n" + "\n".join(
                f"- {inst}" for inst in custom_instructions
            )
            user_prompt += custom_section
        
        return {
            "file_path": str(code_file.relative_path),
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "framework": self.framework,
            "metadata": {
                "line_count": code_file.line_count,
                "functions": len(code_file.functions),
                "classes": len(code_file.classes)
            }
        }
    
    def _get_framework_instructions(self) -> str:
        """
        Get framework-specific instructions (Task 37 requirement).
        
        Returns:
            Framework-specific instructions
        """
        if self.framework == "pytest":
            return """
## Pytest Framework Instructions:

Use pytest conventions:
- Test functions: `def test_function_name():`
- Test classes: `class TestClassName:`
- Fixtures: Use `@pytest.fixture` for setup
- Assertions: Use plain `assert` statements
- Parametrize: Use `@pytest.mark.parametrize` for multiple inputs
- Exceptions: Use `pytest.raises(ExceptionType)`
- Mocking: Use `pytest-mock` or `unittest.mock`

Example test structure:
```python
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_example(sample_data):
    assert sample_data["key"] == "value"

def test_raises_error():
    with pytest.raises(ValueError):
        raise ValueError("test")
```
"""
        elif self.framework == "unittest":
            return """
## Unittest Framework Instructions:

Use unittest conventions:
- Test classes: Inherit from `unittest.TestCase`
- Test methods: Start with `test_`
- Setup: Use `setUp()` and `tearDown()` methods
- Assertions: Use `self.assertEqual()`, `self.assertTrue()`, etc.
- Exceptions: Use `self.assertRaises(ExceptionType)`
- Mocking: Use `unittest.mock`

Example test structure:
```python
import unittest
from unittest.mock import Mock

class TestExample(unittest.TestCase):
    def setUp(self):
        self.data = {"key": "value"}
    
    def test_example(self):
        self.assertEqual(self.data["key"], "value")
    
    def test_raises_error(self):
        with self.assertRaises(ValueError):
            raise ValueError("test")
```
"""
        else:
            return ""
    
    def _insert_code_context(self, prompt: str, code_file: CodeFile) -> str:
        """
        Insert code context into template (Task 37 requirement).
        
        Args:
            prompt: Prompt template
            code_file: Code file to insert
            
        Returns:
            Prompt with inserted context
        """
        # Already handled by PromptBuilder.format(),
        # but we can add additional context if needed
        return prompt
    
    def get_statistics(self, scan_result: ScanResult) -> Dict[str, any]:
        """
        Get statistics about prompts that would be generated.
        
        Args:
            scan_result: Scan result to analyze
            
        Returns:
            Statistics dictionary
        """
        prompts = self.build_prompt(scan_result)
        
        total_chars = sum(
            len(p["system_prompt"]) + len(p["user_prompt"])
            for p in prompts
        )
        
        avg_prompt_size = total_chars // len(prompts) if prompts else 0
        
        return {
            "total_files": len(prompts),
            "total_functions": sum(p["metadata"]["functions"] for p in prompts),
            "total_classes": sum(p["metadata"]["classes"] for p in prompts),
            "total_lines": sum(p["metadata"]["line_count"] for p in prompts),
            "total_prompt_chars": total_chars,
            "avg_prompt_chars": avg_prompt_size,
            "framework": self.framework,
            "coverage_target": self.coverage_target
        }


# Convenience function for quick access
def build_prompts_from_scan(
    scan_result: ScanResult,
    framework: str = "pytest",
    coverage_target: int = 80,
    include_examples: bool = False
) -> List[Dict[str, str]]:
    """
    Quick function to build prompts from scan result.
    
    Args:
        scan_result: ScanResult from scanner
        framework: Test framework (pytest or unittest)
        coverage_target: Target coverage percentage
        include_examples: Include few-shot examples
        
    Returns:
        List of prompt dictionaries
        
    Example:
        >>> from testgen.core.scanner import CodeScanner
        >>> scanner = CodeScanner()
        >>> result = scanner.scan_directory("./src")
        >>> prompts = build_prompts_from_scan(result, framework="pytest")
    """
    builder = AdvancedPromptBuilder(
        framework=framework,
        coverage_target=coverage_target,
        include_examples=include_examples
    )
    return builder.build_prompt(scan_result)

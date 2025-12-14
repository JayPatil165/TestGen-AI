"""
Test Prompt Generator for TestGen AI.

This module handles the creation of prompts for test generation by combining
code context from the scanner with prompt templates.
"""

from pathlib import Path
from typing import Optional, List

from testgen.core.scanner import CodeFile, ScanResult
from testgen.prompts import (
    get_system_instruction,
    get_test_generation_prompt,
    PromptBuilder
)


class TestPromptGenerator:
    """
    Generates complete prompts for test generation.
    
    Combines scanned code context with prompt templates to create
    comprehensive prompts for LLMs.
    
    Example:
        >>> generator = TestPromptGenerator()
        >>> prompt = generator.generate_for_file(code_file)
        >>> system_prompt = generator.get_system_prompt()
    """
    
    def __init__(
        self,
        include_examples: bool = False,
        coverage_target: int = 80,
        framework: str = "pytest"
    ):
        """
        Initialize prompt generator.
        
        Args:
            include_examples: Whether to include few-shot examples
            coverage_target: Target test coverage percentage
            framework: Test framework to use (default: pytest)
        """
        self.include_examples = include_examples
        self.coverage_target = coverage_target
        self.framework = framework
    
    def get_system_prompt(self) -> str:
        """
        Get the system instruction for test generation.
        
        Returns:
            System instruction content
        """
        return get_system_instruction()
    
    def generate_for_file(
        self,
        code_file: CodeFile,
        include_imports: bool = True,
        include_structure: bool = True
    ) -> str:
        """
        Generate a test prompt for a single code file.
        
        Args:
            code_file: CodeFile object from scanner
            include_imports: Include import statements in context
            include_structure: Include file structure info
            
        Returns:
            Complete prompt for test generation
        """
        # Build code context
        context_parts = []
        
        # Add file information
        if include_structure:
            context_parts.append(f"# File: {code_file.relative_path}")
            context_parts.append(f"# Type: {code_file.file_type.value}")
            context_parts.append(f"# Lines: {code_file.line_count}")
            context_parts.append("")
        
        # Add imports
        if include_imports and code_file.imports:
            context_parts.append("# Imports:")
            for imp in code_file.imports[:10]:  # Limit to top 10
                context_parts.append(f"#   {imp}")
            context_parts.append("")
        
        # Add code content
        if code_file.content:
            context_parts.append(code_file.content)
        else:
            # If no full content, build from extracted info
            context_parts.extend(self._build_context_from_metadata(code_file))
        
        code_context = "\n".join(context_parts)
        
        # Generate prompt using builder
        prompt = (
            PromptBuilder(code_context)
            .with_file_path(str(code_file.relative_path))
            .with_framework(self.framework)
            .with_coverage_target(self.coverage_target)
        )
        
        if self.include_examples:
            prompt = prompt.with_examples()
        
        return prompt.build()
    
    def generate_for_function(
        self,
        code_file: CodeFile,
        function_name: str
    ) -> str:
        """
        Generate a prompt for testing a specific function.
        
        Args:
            code_file: CodeFile containing the function
            function_name: Name of function to test
            
        Returns:
            Prompt focused on the specific function
        """
        # Find the function
        func_info = next(
            (f for f in code_file.functions if f["name"] == function_name),
            None
        )
        
        if not func_info:
            raise ValueError(f"Function '{function_name}' not found in {code_file.path}")
        
        # Build context with just this function
        context_parts = [
            f"# Function from {code_file.relative_path}",
            "",
            func_info.get("signature", f"def {function_name}(...):"),
        ]
        
        code_context = "\n".join(context_parts)
        
        return (
            PromptBuilder(code_context)
            .with_file_path(f"{code_file.relative_path}::{function_name}")
            .with_framework(self.framework)
            .with_custom_instruction(f"Focus only on testing the '{function_name}' function")
            .build()
        )
    
    def generate_for_class(
        self,
        code_file: CodeFile,
        class_name: str
    ) -> str:
        """
        Generate a prompt for testing a specific class.
        
        Args:
            code_file: CodeFile containing the class
            class_name: Name of class to test
            
        Returns:
            Prompt focused on the specific class
        """
        # Find the class
        class_info = next(
            (c for c in code_file.classes if c["name"] == class_name),
            None
        )
        
        if not class_info:
            raise ValueError(f"Class '{class_name}' not found in {code_file.path}")
        
        # Build context
        context_parts = [
            f"# Class from {code_file.relative_path}",
            "",
            f"class {class_name}:",
        ]
        
        # Add methods
        for method in class_info.get("methods", []):
            context_parts.append(f"    {method}")
        
        code_context = "\n".join(context_parts)
        
        return (
            PromptBuilder(code_context)
            .with_file_path(f"{code_file.relative_path}::{class_name}")
            .with_framework(self.framework)
            .with_custom_instruction(f"Focus on testing the '{class_name}' class and all its methods")
            .build()
        )
    
    def generate_batch(
        self,
        code_files: List[CodeFile],
        max_files: int = 5
    ) -> List[tuple[str, str]]:
        """
        Generate prompts for multiple files.
        
        Args:
            code_files: List of CodeFile objects
            max_files: Maximum number of files to process
            
        Returns:
            List of (file_path, prompt) tuples
        """
        results = []
        
        for code_file in code_files[:max_files]:
            try:
                prompt = self.generate_for_file(code_file)
                results.append((str(code_file.relative_path), prompt))
            except Exception as e:
                # Log error but continue
                print(f"Warning: Failed to generate prompt for {code_file.path}: {e}")
        
        return results
    
    def _build_context_from_metadata(self, code_file: CodeFile) -> List[str]:
        """
        Build code context from metadata when full content is not available.
        
        Args:
            code_file: CodeFile with metadata
            
        Returns:
            List of context lines
        """
        context = []
        
        # Add functions
        if code_file.functions:
            context.append("# Functions:")
            for func in code_file.functions:
                signature = func.get("signature", f"def {func['name']}(...):")
                context.append(signature)
                if func.get("docstring"):
                    context.append(f'    """{func["docstring"]}"""')
                context.append("")
        
        # Add classes
        if code_file.classes:
            context.append("# Classes:")
            for cls in code_file.classes:
                context.append(f"class {cls['name']}:")
                if cls.get("docstring"):
                    context.append(f'    """{cls["docstring"]}"""')
                
                # Add methods
                for method in cls.get("methods", []):
                    context.append(f"    {method}")
                context.append("")
        
        return context


def create_prompt_for_scan_result(
    scan_result: ScanResult,
    file_filter: Optional[str] = None,
    include_examples: bool = False
) -> List[tuple[str, str, str]]:
    """
    Create prompts for all files in a scan result.
    
    Args:
        scan_result: ScanResult from scanner
        file_filter: Optional glob pattern to filter files
        include_examples: Whether to include few-shot examples
        
    Returns:
        List of (file_path, system_prompt, user_prompt) tuples
        
    Example:
        >>> from testgen.core.scanner import CodeScanner
        >>> scanner = CodeScanner()
        >>> result = scanner.scan_directory("./src")
        >>> prompts = create_prompt_for_scan_result(result)
        >>> for file_path, system, user in prompts:
        ...     # Send to LLM for test generation
        ...     pass
    """
    generator = TestPromptGenerator(include_examples=include_examples)
    system_prompt = generator.get_system_prompt()
    
    results = []
    
    for code_file in scan_result.files:
        # Apply filter if specified
        if file_filter and not Path(code_file.path).match(file_filter):
            continue
        
        # Skip files without content (e.g., signatures only for large files)
        if not code_file.content and not (code_file.functions or code_file.classes):
            continue
        
        try:
            user_prompt = generator.generate_for_file(code_file)
            results.append((
                str(code_file.relative_path),
                system_prompt,
                user_prompt
            ))
        except Exception as e:
            print(f"Warning: Skipping {code_file.path}: {e}")
    
    return results

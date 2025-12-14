"""
Response Validation and Code Extraction for TestGen AI.

This module handles validation of LLM responses, ensuring they contain
valid Python code and extracting code from markdown blocks.
"""

import re
import ast
from typing import Optional, List, Tuple
from pydantic import BaseModel, Field, field_validator


class TestCodeValidation(BaseModel):
    """
    Validation result for generated test code.
    
    Attributes:
        is_valid: Whether code is valid
        code: Extracted/cleaned code
        syntax_valid: Whether Python syntax is valid
        has_tests: Whether code contains test functions/classes
        has_imports: Whether code has import statements
        issues: List of validation issues found
        warnings: List of warnings (non-critical)
    """
    
    is_valid: bool = Field(..., description="Whether code passes all validation")
    code: str = Field(..., description="Extracted and cleaned code")
    syntax_valid: bool = Field(default=False, description="Python syntax validity")
    has_tests: bool = Field(default=False, description="Contains test functions/classes")
    has_imports: bool = Field(default=False, description="Has import statements")
    issues: List[str] = Field(default_factory=list, description="Validation issues")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")
    
    @property
    def test_count(self) -> int:
        """Count number of test functions/methods in code."""
        if not self.syntax_valid:
            return 0
        
        try:
            tree = ast.parse(self.code)
            count = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        count += 1
                elif isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        # Count methods in test class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                                count += 1
            
            return count
        except:
            return 0
    
    def __str__(self) -> str:
        """String representation of validation result."""
        status = "✓ VALID" if self.is_valid else "✗ INVALID"
        details = [
            f"Status: {status}",
            f"Syntax: {'✓' if self.syntax_valid else '✗'}",
            f"Tests: {'✓' if self.has_tests else '✗'} ({self.test_count} found)",
            f"Imports: {'✓' if self.has_imports else '✗'}",
        ]
        
        if self.issues:
            details.append(f"Issues: {len(self.issues)}")
        if self.warnings:
            details.append(f"Warnings: {len(self.warnings)}")
        
        return " | ".join(details)


class ResponseValidator:
    """
    Validates LLM responses and extracts test code.
    
    Implements Task 39 requirements:
    - Define expected output schema
    - Validate LLM returns valid Python code
    - Extract code from markdown blocks
    
    Example:
        >>> validator = ResponseValidator()
        >>> result = validator.validate_response(llm_output)
        >>> if result.is_valid:
        ...     print(result.code)
    """
    
    def __init__(
        self,
        require_tests: bool = True,
        require_imports: bool = False,
        allow_warnings: bool = True
    ):
        """
        Initialize response validator.
        
        Args:
            require_tests: Whether to require test functions
            require_imports: Whether to require import statements
            allow_warnings: Whether to allow warnings (non-critical issues)
        """
        self.require_tests = require_tests
        self.require_imports = require_imports
        self.allow_warnings = allow_warnings
    
    def validate_response(self, response: str) -> TestCodeValidation:
        """
        Validate LLM response and extract code (Task 39 requirement).
        
        Args:
            response: Raw LLM response
            
        Returns:
            TestCodeValidation with validation results and extracted code
            
        Example:
            >>> validator = ResponseValidator()
            >>> result = validator.validate_response(llm_output)
            >>> print(result)
        """
        issues = []
        warnings = []
        
        # Step 1: Extract code from markdown blocks
        code = self._extract_code_from_markdown(response)
        
        if not code:
            # No markdown blocks, try to use whole response
            code = response.strip()
            warnings.append("No markdown code blocks found, using raw response")
        
        # Step 2: Clean code
        code = self._clean_code(code)
        
        # Step 3: Validate Python syntax
        syntax_valid = self._validate_syntax(code)
        if not syntax_valid:
            issues.append("Invalid Python syntax")
        
        # Step 4: Check for test functions/classes
        has_tests = self._has_test_functions(code)
        if self.require_tests and not has_tests:
            issues.append("No test functions found (must start with 'test_' or be in 'Test' class)")
        
        # Step 5: Check for imports
        has_imports = self._has_imports(code)
        if self.require_imports and not has_imports:
            issues.append("No import statements found")
        
        # Step 6: Check for common issues
        code_warnings = self._check_code_quality(code)
        warnings.extend(code_warnings)
        
        # Determine overall validity
        is_valid = syntax_valid and (not issues or (self.allow_warnings and not any("Invalid" in i for i in issues)))
        if self.require_tests:
            is_valid = is_valid and has_tests
        
        return TestCodeValidation(
            is_valid=is_valid,
            code=code,
            syntax_valid=syntax_valid,
            has_tests=has_tests,
            has_imports=has_imports,
            issues=issues,
            warnings=warnings
        )
    
    def _extract_code_from_markdown(self, text: str) -> str:
        """
        Extract code from markdown code blocks (Task 39 requirement).
        
        Supports:
        - ```python ... ```
        - ``` ... ```
        - ```py ... ```
        
        Args:
            text: Text with markdown code blocks
            
        Returns:
            Extracted code or empty string
        """
        # Pattern for markdown code blocks
        patterns = [
            r'```python\n(.*?)```',
            r'```py\n(.*?)```',
            r'```\n(.*?)```',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                # Join all code blocks
                return '\n\n'.join(matches)
        
        return ""
    
    def _clean_code(self, code: str) -> str:
        """
        Clean extracted code.
        
        Args:
            code: Raw code
            
        Returns:
            Cleaned code
        """
        # Remove common LLM artifacts
        code = code.strip()
        
        # Remove leading/trailing quotes if present
        if code.startswith(('"""', "'''")):
            code = code[3:]
        if code.endswith(('"""', "'''")):
            code = code[:-3]
        
        # Remove common explanatory text
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that look like explanations
            if line.strip().startswith(('#', '//')) and any(
                keyword in line.lower() 
                for keyword in ['note:', 'explanation:', 'this is', 'here is']
            ):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _validate_syntax(self, code: str) -> bool:
        """
        Validate Python syntax (Task 39 requirement).
        
        Args:
            code: Python code
            
        Returns:
            True if syntax is valid
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def _has_test_functions(self, code: str) -> bool:
        """
        Check if code has test functions.
        
        Args:
            code: Python code
            
        Returns:
            True if test functions found
        """
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for test functions
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        return True
                
                # Check for test classes
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        return True
            
            return False
        except:
            return False
    
    def _has_imports(self, code: str) -> bool:
        """
        Check if code has import statements.
        
        Args:
            code: Python code
            
        Returns:
            True if imports found
        """
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    return True
            
            return False
        except:
            return False
    
    def _check_code_quality(self, code: str) -> List[str]:
        """
        Check code for quality issues.
        
        Args:
            code: Python code
            
        Returns:
            List of warnings
        """
        warnings = []
        
        # Check for TODO/FIXME comments
        if 'TODO' in code or 'FIXME' in code:
            warnings.append("Contains TODO/FIXME comments")
        
        # Check for placeholder code
        if 'pass' in code:
            pass_count = code.count('pass')
            if pass_count > 2:
                warnings.append(f"Multiple 'pass' statements ({pass_count}) - may be incomplete")
        
        # Check for print statements (not ideal in tests)
        if 'print(' in code:
            warnings.append("Contains print() statements")
        
        # Check code length
        lines = code.split('\n')
        if len(lines) < 5:
            warnings.append("Very short test code (< 5 lines)")
        
        return warnings
    
    def batch_validate(self, responses: List[str]) -> List[TestCodeValidation]:
        """
        Validate multiple responses.
        
        Args:
            responses: List of LLM responses
            
        Returns:
            List of validation results
        """
        return [self.validate_response(r) for r in responses]
    
    def get_statistics(self, validations: List[TestCodeValidation]) -> dict:
        """
        Get statistics from multiple validations.
        
        Args:
            validations: List of validation results
            
        Returns:
            Statistics dictionary
        """
        total = len(validations)
        if total == 0:
            return {}
        
        valid = sum(1 for v in validations if v.is_valid)
        syntax_valid = sum(1 for v in validations if v.syntax_valid)
        has_tests = sum(1 for v in validations if v.has_tests)
        total_tests = sum(v.test_count for v in validations)
        
        return {
            "total_responses": total,
            "valid_responses": valid,
            "syntax_valid": syntax_valid,
            "has_tests": has_tests,
            "total_tests": total_tests,
            "avg_tests_per_response": total_tests / total if total > 0 else 0,
            "validation_rate": f"{valid / total * 100:.1f}%",
            "syntax_rate": f"{syntax_valid / total * 100:.1f}%"
        }


def validate_test_code(code: str) -> TestCodeValidation:
    """
    Quick function to validate test code.
    
    Args:
        code: Test code to validate
        
    Returns:
        Validation result
        
    Example:
        >>> result = validate_test_code(generated_tests)
        >>> if result.is_valid:
        ...     save_to_file(result.code)
    """
    validator = ResponseValidator()
    return validator.validate_response(code)

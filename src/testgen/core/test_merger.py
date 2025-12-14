"""
Smart Test Merging for TestGen AI.

This module handles intelligent merging of new tests into existing test files,
avoiding duplicates while preserving manually written tests.
"""

import ast
from typing import List, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MergeResult:
    """Result of merging tests."""
    
    merged_code: str
    tests_added: int
    tests_skipped: int
    tests_preserved: int
    duplicates_avoided: List[str]
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"[MERGE] Added: {self.tests_added}, "
            f"Skipped: {self.tests_skipped}, "
            f"Preserved: {self.tests_preserved}"
        )


class TestMerger:
    """
    Intelligently merges new tests into existing test files.
    
    Implements Task 42 requirements:
    - Merge new tests into existing files
    - Avoid duplicates
    - Preserve manually written tests
    
    Example:
        >>> merger = TestMerger()
        >>> result = merger.merge_tests(
        ...     existing_code=old_tests,
        ...     new_code=generated_tests
        ... )
        >>> print(result)
    """
    
    def __init__(self, preserve_comments: bool = True):
        """
        Initialize test merger.
        
        Args:
            preserve_comments: Whether to preserve comments from existing tests
        """
        self.preserve_comments = preserve_comments
    
    def merge_tests(
        self,
        existing_code: str,
        new_code: str
    ) -> MergeResult:
        """
        Merge new tests into existing code (Task 42 requirement).
        
        Args:
            existing_code: Existing test file content
            new_code: New generated tests
            
        Returns:
            MergeResult with merged code and statistics
            
        Example:
            >>> merger = TestMerger()
            >>> result = merger.merge_tests(existing, new)
            >>> save_file(result.merged_code)
        """
        # Extract test functions from both
        existing_tests = self._extract_tests(existing_code)
        new_tests = self._extract_tests(new_code)
        
        # Get test names
        existing_names = {t['name'] for t in existing_tests}
        new_names = {t['name'] for t in new_tests}
        
        # Find duplicates and unique tests
        duplicates = existing_names & new_names
        unique_new = [t for t in new_tests if t['name'] not in existing_names]
        
        # Build merged code
        merged_code = self._build_merged_code(
            existing_code,
            unique_new,
            new_code
        )
        
        return MergeResult(
            merged_code=merged_code,
            tests_added=len(unique_new),
            tests_skipped=len(duplicates),
            tests_preserved=len(existing_tests),
            duplicates_avoided=list(duplicates)
        )
    
    def _extract_tests(self, code: str) -> List[dict]:
        """
        Extract test functions and classes from code.
        
        Args:
            code: Python test code
            
        Returns:
            List of test information dicts
        """
        tests = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Extract test functions
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        tests.append({
                            'name': node.name,
                            'type': 'function',
                            'lineno': node.lineno,
                            'end_lineno': node.end_lineno if hasattr(node, 'end_lineno') else None
                        })
                
                # Extract test classes
                elif isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        # Get all test methods in class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                                tests.append({
                                    'name': f"{node.name}.{item.name}",
                                    'type': 'method',
                                    'class': node.name,
                                    'lineno': item.lineno,
                                    'end_lineno': item.end_lineno if hasattr(item, 'end_lineno') else None
                                })
        except:
            pass
        
        return tests
    
    def _build_merged_code(
        self,
        existing_code: str,
        new_tests: List[dict],
        new_code: str
    ) -> str:
        """
        Build merged code by appending new tests to existing.
        
        Args:
            existing_code: Existing test code
            new_tests: List of new test info dicts
            new_code: Full new test code
            
        Returns:
            Merged code
        """
        if not new_tests:
            # No new tests to add
            return existing_code
        
        # Extract the actual test functions from new_code
        new_test_code = self._extract_test_code(new_code, new_tests)
        
        # Append to existing
        merged = existing_code.rstrip()
        
        # Add separator
        merged += "\n\n# Auto-generated tests added below\n"
        merged += f"# Generated: {self._get_timestamp()}\n\n"
        
        # Add new tests
        merged += new_test_code
        
        return merged
    
    def _extract_test_code(self, code: str, tests: List[dict]) -> str:
        """
        Extract specific test functions from code.
        
        Args:
            code: Full code
            tests: List of tests to extract
            
        Returns:
            Code containing only specified tests
        """
        if not tests:
            return ""
        
        lines = code.split('\n')
        extracted = []
        
        try:
            tree = ast.parse(code)
            
            for test_info in tests:
                # Find the corresponding node
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name == test_info['name']:
                            # Extract lines for this function
                            start = node.lineno - 1
                            end = node.end_lineno if hasattr(node, 'end_lineno') else start + 10
                            
                            # Add function with proper indentation
                            func_lines = lines[start:end]
                            extracted.append('\n'.join(func_lines))
                            break
        except:
            # Fallback: just append the new code
            return code
        
        return '\n\n'.join(extracted)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def find_duplicates(
        self,
        existing_code: str,
        new_code: str
    ) -> List[str]:
        """
        Find duplicate test names (Task 42 requirement).
        
        Args:
            existing_code: Existing tests
            new_code: New tests
            
        Returns:
            List of duplicate test names
        """
        existing_tests = self._extract_tests(existing_code)
        new_tests = self._extract_tests(new_code)
        
        existing_names = {t['name'] for t in existing_tests}
        new_names = {t['name'] for t in new_tests}
        
        return list(existing_names & new_names)
    
    def preserve_manual_tests(
        self,
        code: str,
        marker: str = "# MANUAL TEST"
    ) -> Tuple[str, List[str]]:
        """
        Identify and preserve manually written tests (Task 42 requirement).
        
        Args:
            code: Test code
            marker: Comment marker for manual tests
            
        Returns:
            (code, list of manual test names)
        """
        manual_tests = []
        lines = code.split('\n')
        
        # Look for manual test markers
        for i, line in enumerate(lines):
            if marker in line:
                # Find the next test function
                for j in range(i, min(i + 10, len(lines))):
                    if 'def test_' in lines[j]:
                        # Extract test name
                        test_name = lines[j].split('def ')[1].split('(')[0]
                        manual_tests.append(test_name)
                        break
        
        return code, manual_tests


def merge_test_files(
    existing_path: str,
    new_code: str
) -> MergeResult:
    """
    Quick function to merge tests into an existing file.
    
    Args:
        existing_path: Path to existing test file
        new_code: New test code to merge
        
    Returns:
        MergeResult
        
    Example:
        >>> result = merge_test_files(
        ...     "tests/test_example.py",
        ...     new_generated_tests
        ... )
        >>> print(f"Added {result.tests_added} tests")
    """
    from pathlib import Path
    
    existing_code = ""
    if Path(existing_path).exists():
        existing_code = Path(existing_path).read_text(encoding='utf-8')
    
    merger = TestMerger()
    return merger.merge_tests(existing_code, new_code)

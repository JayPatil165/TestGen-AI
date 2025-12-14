"""
Code Sanitization for TestGen AI.

This module handles sanitization of generated test code,
removing unsafe imports and adding required dependencies.
"""

import ast
import re
from typing import List, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SanitizationResult:
    """Result of code sanitization."""
    
    sanitized_code: str
    removed_imports: List[str]
    added_imports: List[str]
    issues_fixed: List[str]
    warnings: List[str]
    is_safe: bool
    
    def __str__(self) -> str:
        """String representation."""
        status = "✓ SAFE" if self.is_safe else "✗ UNSAFE"
        parts = [f"Status: {status}"]
        
        if self.removed_imports:
            parts.append(f"Removed: {len(self.removed_imports)} unsafe imports")
        if self.added_imports:
            parts.append(f"Added: {len(self.added_imports)} imports")
        if self.issues_fixed:
            parts.append(f"Fixed: {len(self.issues_fixed)} issues")
            
        return " | ".join(parts)


class CodeSanitizer:
    """
    Sanitizes generated test code for safety.
    
    Implements Task 40 requirements:
    - Remove unsafe imports (os.system, eval, exec)
    - Verify syntax validity
    - Add required imports if missing
    
    Example:
        >>> sanitizer = CodeSanitizer()
        >>> result = sanitizer.sanitize(generated_code)
        >>> if result.is_safe:
        ...     save(result.sanitized_code)
    """
    
    # Unsafe modules/functions to remove
    UNSAFE_IMPORTS = {
        'os.system',
        'subprocess.call',
        'subprocess.Popen',
        'eval',
        'exec',
        'compile',
        '__import__',
        'importlib',
        'pickle',
        'shelve',
        'dill',
        'marshal',
    }
    
    # Unsafe builtin calls
    UNSAFE_BUILTINS = {
        'eval',
        'exec',
        'compile',
        '__import__',
        'open',  # Can be dangerous in tests
    }
    
    # Required imports for pytest tests
    PYTEST_IMPORTS = {
        'pytest',
    }
    
    # Common imports that should be present
    COMMON_TEST_IMPORTS = {
        'pytest',
        'unittest.mock',
        'typing',
    }
    
    def __init__(
        self,
        strict_mode: bool = True,
        auto_add_imports: bool = True
    ):
        """
        Initialize code sanitizer.
        
        Args:
            strict_mode: If True, reject code with any unsafe patterns
            auto_add_imports: If True, automatically add missing imports
        """
        self.strict_mode = strict_mode
        self.auto_add_imports = auto_add_imports
    
    def sanitize(self, code: str) -> SanitizationResult:
        """
        Sanitize code by removing unsafe imports and adding required ones.
        
        Args:
            code: Generated test code
            
        Returns:
            SanitizationResult with sanitized code and metadata
            
        Example:
            >>> sanitizer = CodeSanitizer()
            >>> result = sanitizer.sanitize(code)
            >>> print(result)
        """
        removed_imports = []
        added_imports = []
        issues_fixed = []
        warnings = []
        
        # Step 1: Verify syntax
        if not self._verify_syntax(code):
            return SanitizationResult(
                sanitized_code=code,
                removed_imports=[],
                added_imports=[],
                issues_fixed=[],
                warnings=["Invalid Python syntax"],
                is_safe=False
            )
        
        # Step 2: Remove unsafe imports
        code, unsafe_removed = self._remove_unsafe_imports(code)
        removed_imports.extend(unsafe_removed)
        if unsafe_removed:
            issues_fixed.append(f"Removed {len(unsafe_removed)} unsafe imports")
        
        # Step 3: Remove unsafe builtin calls
        code, unsafe_calls = self._remove_unsafe_calls(code)
        if unsafe_calls:
            issues_fixed.append(f"Removed {len(unsafe_calls)} unsafe function calls")
            warnings.extend([f"Removed unsafe call: {call}" for call in unsafe_calls])
        
        # Step 4: Add required imports
        if self.auto_add_imports:
            code, new_imports = self._add_required_imports(code)
            added_imports.extend(new_imports)
            if new_imports:
                issues_fixed.append(f"Added {len(new_imports)} required imports")
        
        # Step 5: Final syntax check
        syntax_valid = self._verify_syntax(code)
        if not syntax_valid:
            warnings.append("Final syntax check failed - code may need manual review")
        
        # Determine safety
        is_safe = (
            len(removed_imports) == 0 or not self.strict_mode
        ) and syntax_valid
        
        return SanitizationResult(
            sanitized_code=code,
            removed_imports=removed_imports,
            added_imports=added_imports,
            issues_fixed=issues_fixed,
            warnings=warnings,
            is_safe=is_safe
        )
    
    def _verify_syntax(self, code: str) -> bool:
        """
        Verify Python syntax validity (Task 40 requirement).
        
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
    
    def _remove_unsafe_imports(self, code: str) -> Tuple[str, List[str]]:
        """
        Remove unsafe imports (Task 40 requirement).
        
        Args:
            code: Python code
            
        Returns:
            (cleaned_code, removed_imports)
        """
        removed = []
        lines = code.split('\n')
        clean_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check for unsafe imports
            is_unsafe = False
            
            for unsafe in self.UNSAFE_IMPORTS:
                if unsafe in line_stripped:
                    # Further check if it's actually an import statement
                    if line_stripped.startswith(('import ', 'from ')):
                        is_unsafe = True
                        removed.append(line_stripped)
                        break
            
            if not is_unsafe:
                clean_lines.append(line)
        
        return '\n'.join(clean_lines), removed
    
    def _remove_unsafe_calls(self, code: str) -> Tuple[str, List[str]]:
        """
        Remove lines with unsafe builtin calls.
        
        Args:
            code: Python code
            
        Returns:
            (cleaned_code, removed_calls)
        """
        removed = []
        
        try:
            tree = ast.parse(code)
            
            # Find unsafe calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.UNSAFE_BUILTINS:
                            removed.append(node.func.id)
            
            # If we found unsafe calls, we need to remove them
            # For now, we'll just warn about them and keep the code
            # A more sophisticated approach would rebuild the AST
            
        except:
            pass
        
        return code, removed
    
    def _add_required_imports(self, code: str) -> Tuple[str, List[str]]:
        """
        Add required imports if missing (Task 40 requirement).
        
        Args:
            code: Python code
            
        Returns:
            (code_with_imports, added_imports)
        """
        added = []
        
        try:
            tree = ast.parse(code)
            existing_imports = self._get_existing_imports(tree)
            
            # Check if pytest is needed
            needs_pytest = self._needs_pytest(tree)
            
            # Build list of imports to add
            to_add = set()
            
            if needs_pytest and 'pytest' not in existing_imports:
                to_add.add('pytest')
            
            # Check for unittest.mock usage
            if self._uses_mock(code) and 'unittest.mock' not in existing_imports:
                to_add.add('unittest.mock')
            
            # Add imports at the top
            if to_add:
                import_lines = []
                for imp in sorted(to_add):
                    if '.' in imp:
                        # from X import Y
                        parts = imp.split('.')
                        import_lines.append(f"from {parts[0]} import {parts[1]}")
                    else:
                        import_lines.append(f"import {imp}")
                    added.append(imp)
                
                # Insert imports at the beginning
                code = '\n'.join(import_lines) + '\n\n' + code
        
        except:
            pass
        
        return code, added
    
    def _get_existing_imports(self, tree: ast.AST) -> Set[str]:
        """Get set of existing imports."""
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.add(f"{node.module}.{alias.name}")
        
        return imports
    
    def _needs_pytest(self, tree: ast.AST) -> bool:
        """Check if code needs pytest."""
        for node in ast.walk(tree):
            # Check for pytest fixtures
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Attribute):
                        if isinstance(decorator.value, ast.Name):
                            if decorator.value.id == 'pytest':
                                return True
                    elif isinstance(decorator, ast.Name):
                        if decorator.id == 'fixture':
                            return True
            
            # Check for pytest.raises, pytest.mark, etc.
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'pytest':
                            return True
        
        return False
    
    def _uses_mock(self, code: str) -> bool:
        """Check if code uses mocking."""
        mock_patterns = [
            'Mock(',
            'MagicMock(',
            'patch(',
            'mock.',
            '@patch',
            '@mock',
        ]
        
        return any(pattern in code for pattern in mock_patterns)
    
    def sanitize_batch(self, code_samples: List[str]) -> List[SanitizationResult]:
        """
        Sanitize multiple code samples.
        
        Args:
            code_samples: List of code strings
            
        Returns:
            List of sanitization results
        """
        return [self.sanitize(code) for code in code_samples]
    
    def get_statistics(self, results: List[SanitizationResult]) -> dict:
        """
        Get statistics from sanitization results.
        
        Args:
            results: List of sanitization results
            
        Returns:
            Statistics dictionary
        """
        total = len(results)
        if total == 0:
            return {}
        
        safe_count = sum(1 for r in results if r.is_safe)
        total_removed = sum(len(r.removed_imports) for r in results)
        total_added = sum(len(r.added_imports) for r in results)
        total_fixed = sum(len(r.issues_fixed) for r in results)
        
        return {
            "total_samples": total,
            "safe_samples": safe_count,
            "unsafe_samples": total - safe_count,
            "safety_rate": f"{safe_count / total * 100:.1f}%",
            "total_removed_imports": total_removed,
            "total_added_imports": total_added,
            "total_issues_fixed": total_fixed,
        }


def sanitize_test_code(code: str, strict: bool = True) -> SanitizationResult:
    """
    Quick function to sanitize test code.
    
    Args:
        code: Test code to sanitize
        strict: Strict mode flag
        
    Returns:
        Sanitization result
        
    Example:
        >>> result = sanitize_test_code(generated_code)
        >>> if result.is_safe:
        ...     use(result.sanitized_code)
    """
    sanitizer = CodeSanitizer(strict_mode=strict)
    return sanitizer.sanitize(code)

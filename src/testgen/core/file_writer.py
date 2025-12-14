"""
Test File Writer for TestGen AI.

This module handles writing generated test code to files,
creating test directories, and following naming conventions.
"""

import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WriteResult:
    """Result of writing a test file."""
    
    file_path: Path
    success: bool
    created_new: bool
    lines_written: int
    error: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation."""
        status = "[SUCCESS]" if self.success else "[FAILED]"
        mode = "created" if self.created_new else "updated"
        return f"{status}: {mode} {self.file_path} ({self.lines_written} lines)"


class TestFileWriter:
    """
    Writes generated test code to files.
    
    Implements Task 41 requirements:
    - save_test_file(code, output_path) method
    - Auto-create tests/ directory
    - Use test_<original_file>.py naming convention
    
    Example:
        >>> writer = TestFileWriter()
        >>> result = writer.save_test_file(
        ...     code=generated_tests,
        ...     source_file="src/utils.py"
        ... )
        >>> print(result)
    """
    
    def __init__(
        self,
        output_dir: str = "tests",
        add_header: bool = True,
        backup_existing: bool = True
    ):
        """
        Initialize test file writer.
        
        Args:
            output_dir: Output directory for tests (default: "tests")
            add_header: Whether to add file header comments
            backup_existing: Whether to backup existing files before overwriting
        """
        self.output_dir = Path(output_dir)
        self.add_header = add_header
        self.backup_existing = backup_existing
    
    def save_test_file(
        self,
        code: str,
        output_path: Optional[str] = None,
        source_file: Optional[str] = None
    ) -> WriteResult:
        """
        Save test code to file (Task 41 requirement).
        
        Args:
            code: Test code to save
            output_path: Explicit output path (optional)
            source_file: Source file being tested (for auto-naming)
            
        Returns:
            WriteResult with file path and status
            
        Example:
            >>> writer = TestFileWriter()
            >>> result = writer.save_test_file(
            ...     code="def test_example(): pass",
            ...     source_file="src/calculator.py"
            ... )
            >>> print(result.file_path)  # tests/test_calculator.py
        """
        try:
            # Determine output path
            if output_path:
                file_path = Path(output_path)
            elif source_file:
                file_path = self._get_test_path(source_file)
            else:
                return WriteResult(
                    file_path=Path(""),
                    success=False,
                    created_new=False,
                    lines_written=0,
                    error="Either output_path or source_file must be provided"
                )
            
            # Auto-create directory (Task 41 requirement)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists
            created_new = not file_path.exists()
            
            # Backup existing file if needed
            if not created_new and self.backup_existing:
                self._backup_file(file_path)
            
            # Add header if requested
            if self.add_header:
                code = self._add_file_header(code, source_file)
            
            # Write file
            file_path.write_text(code, encoding='utf-8')
            
            # Count lines
            lines_written = len(code.split('\n'))
            
            return WriteResult(
                file_path=file_path,
                success=True,
                created_new=created_new,
                lines_written=lines_written
            )
            
        except Exception as e:
            return WriteResult(
                file_path=file_path if 'file_path' in locals() else Path(""),
                success=False,
                created_new=False,
                lines_written=0,
                error=str(e)
            )
    
    def _get_test_path(self, source_file: str) -> Path:
        """
        Get test file path from source file (Task 41 requirement).
        
        Uses naming convention: test_<original_file>.py
        
        Args:
            source_file: Source file path
            
        Returns:
            Path to test file
            
        Example:
            >>> writer = TestFileWriter()
            >>> writer._get_test_path("src/utils.py")
            Path('tests/test_utils.py')
        """
        source_path = Path(source_file)
        
        # Get base name without extension
        base_name = source_path.stem
        
        # Create test file name
        test_name = f"test_{base_name}.py"
        
        # Preserve directory structure relative to src
        # e.g., src/core/scanner.py -> tests/core/test_scanner.py
        relative_dir = ""
        if "src" in source_path.parts:
            # Get parts after 'src'
            src_index = source_path.parts.index("src")
            if src_index + 1 < len(source_path.parts) - 1:
                relative_dir = Path(*source_path.parts[src_index + 1:-1])
        
        # Build final path
        if relative_dir:
            return self.output_dir / relative_dir / test_name
        else:
            return self.output_dir / test_name
    
    def _add_file_header(self, code: str, source_file: Optional[str] = None) -> str:
        """
        Add header comment to test file.
        
        Args:
            code: Test code
            source_file: Source file path
            
        Returns:
            Code with header
        """
        lines = [
            '"""',
            'Auto-generated test file.',
            ''
        ]
        
        if source_file:
            lines.append(f'Tests for: {source_file}')
        
        lines.extend([
            f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'Generator: TestGen AI',
            '',
            'Feel free to modify these tests as needed.',
            '"""',
            ''
        ])
        
        return '\n'.join(lines) + '\n' + code
    
    def _backup_file(self, file_path: Path) -> None:
        """
        Create backup of existing file.
        
        Args:
            file_path: File to backup
        """
        if not file_path.exists():
            return
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
        backup_path = file_path.parent / backup_name
        
        # Copy file
        backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
    
    def save_batch(
        self,
        tests: List[tuple[str, str]]
    ) -> List[WriteResult]:
        """
        Save multiple test files.
        
        Args:
            tests: List of (code, source_file) tuples
            
        Returns:
            List of WriteResult objects
            
        Example:
            >>> tests = [
            ...     ("def test_a(): pass", "src/a.py"),
            ...     ("def test_b(): pass", "src/b.py")
            ... ]
            >>> results = writer.save_batch(tests)
        """
        results = []
        
        for code, source_file in tests:
            result = self.save_test_file(code=code, source_file=source_file)
            results.append(result)
        
        return results
    
    def get_statistics(self, results: List[WriteResult]) -> dict:
        """
        Get statistics from write results.
        
        Args:
            results: List of write results
            
        Returns:
            Statistics dictionary
        """
        total = len(results)
        if total == 0:
            return {}
        
        successful = sum(1 for r in results if r.success)
        created = sum(1 for r in results if r.created_new)
        updated = sum(1 for r in results if r.success and not r.created_new)
        failed = sum(1 for r in results if not r.success)
        total_lines = sum(r.lines_written for r in results if r.success)
        
        return {
            "total_files": total,
            "successful": successful,
            "created_new": created,
            "updated_existing": updated,
            "failed": failed,
            "success_rate": f"{successful / total * 100:.1f}%",
            "total_lines_written": total_lines
        }
    
    def create_test_structure(
        self,
        project_root: str = "."
    ) -> None:
        """
        Create standard test directory structure.
        
        Creates:
        - tests/
        - tests/__init__.py
        - tests/fixtures/
        - tests/conftest.py (pytest configuration)
        
        Args:
            project_root: Project root directory
        """
        root = Path(project_root)
        tests_dir = root / self.output_dir
        
        # Create directories
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "fixtures").mkdir(exist_ok=True)
        
        # Create __init__.py
        (tests_dir / "__init__.py").touch()
        
        # Create conftest.py with basic pytest configuration
        conftest_content = '''"""
Pytest configuration and fixtures.

This file is automatically loaded by pytest.
"""

import pytest

# Add your global fixtures here
'''
        (tests_dir / "conftest.py").write_text(conftest_content, encoding='utf-8')


def save_test_file(
    code: str,
    output_path: Optional[str] = None,
    source_file: Optional[str] = None,
    output_dir: str = "tests"
) -> WriteResult:
    """
    Quick function to save a test file.
    
    Args:
        code: Test code
        output_path: Explicit output path
        source_file: Source file path
        output_dir: Output directory
        
    Returns:
        WriteResult
        
    Example:
        >>> result = save_test_file(
        ...     code="def test_example(): pass",
        ...     source_file="src/example.py"
        ... )
    """
    writer = TestFileWriter(output_dir=output_dir)
    return writer.save_test_file(code=code, output_path=output_path, source_file=source_file)

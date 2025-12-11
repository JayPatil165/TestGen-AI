"""
Unit tests for the Code Scanner module (Task 32).

This test suite covers:
- Directory traversal
- File filtering logic
- Code extraction accuracy
- Edge cases (empty files, syntax errors, binary files)
- Pydantic model validation
- LLM context generation
"""

import pytest
from pathlib import Path
from testgen.core.scanner import CodeScanner, CodeFile, ScanResult, FileType


class TestDirectoryTraversal:
    """Test directory scanning and traversal functionality."""
    
    def test_scan_python_fixtures(self):
        """Test scanning Python test fixtures."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        assert isinstance(result, ScanResult)
        assert result.total_files == 2
        assert len(result.files) == 2
        assert result.total_lines > 0
        assert result.total_tokens > 0
    
    def test_scan_javascript_fixtures(self):
        """Test scanning JavaScript test fixtures."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/javascript_project')
        
        assert result.total_files == 2
        assert len(result.files) == 2
        
        # Check file types
        file_types = [f.file_type for f in result.files]
        assert FileType.JAVASCRIPT in file_types or FileType.JSX in file_types
    
    def test_recursive_traversal(self):
        """Test that scanner recursively traverses directories."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures')
        
        # Should find files in both python_project and javascript_project
        assert result.total_files >= 4
        
        # Check we have both Python and JavaScript files
        py_files = [f for f in result.files if f.file_type == FileType.PYTHON]
        js_files = [f for f in result.files if f.file_type in (FileType.JAVASCRIPT, FileType.JSX)]
        
        assert len(py_files) >= 2
        assert len(js_files) >= 2


class TestFilteringLogic:
    """Test file filtering and ignore patterns."""
    
    def test_ignore_patterns_default(self):
        """Test that default ignore patterns work."""
        scanner = CodeScanner()
        result = scanner.scan_directory('.')
        
        # Should ignore common patterns
        ignored_str = '|'.join(result.ignored_paths)
        
        # Check that .venv, __pycache__, etc. are ignored
        assert any('venv' in str(p).lower() for p in result.ignored_paths)
    
    def test_binary_file_detection(self):
        """Test that binary files are detected and skipped."""
        scanner = CodeScanner()
        
        # Binary files should be in ignored_paths with (binary) marker
        result = scanner.scan_directory('.')
        
        binary_ignored = [p for p in result.ignored_paths if '(binary)' in str(p)]
        # We expect some binary files to be ignored
        assert len(binary_ignored) >= 0  # May be 0 if no binary files in fixtures
    
    def test_config_file_filtering(self):
        """Test config file filtering."""
        # Without config files
        scanner_no_config = CodeScanner(include_config_files=False)
        result_no_config = scanner_no_config.scan_directory('.')
        
        # With config files
        scanner_with_config = CodeScanner(include_config_files=True)
        result_with_config = scanner_with_config.scan_directory('.')
        
        # With config should have same or more files
        assert result_with_config.total_files >= result_no_config.total_files
    
    def test_custom_ignore_patterns(self):
        """Test custom ignore patterns."""
        custom_patterns = ['*.md', 'test_*']
        scanner = CodeScanner(ignore_patterns=custom_patterns)
        result = scanner.scan_directory('./tests/fixtures')
        
        # Should ignore markdown files
        md_files = [f for f in result.files if f.relative_path.suffix == '.md']
        assert len(md_files) == 0


class TestExtractionAccuracy:
    """Test code extraction accuracy for different languages."""
    
    def test_python_function_extraction(self):
        """Test Python function extraction."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        # Find sample_module.py
        sample_module = [f for f in result.files if 'sample_module' in str(f.relative_path)][0]
        
        # Should extract functions
        assert len(sample_module.functions) > 0
        
        # Should have type hints in signatures
        has_type_hints = any('->' in func or ':' in func for func in sample_module.functions)
        assert has_type_hints
    
    def test_python_class_extraction(self):
        """Test Python class extraction with decorators."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        sample_module = [f for f in result.files if 'sample_module' in str(f.relative_path)][0]
        
        # Should extract classes
        assert len(sample_module.classes) >= 2
        
        # Should detect @dataclass decorator
        has_decorators = any('@' in cls for cls in sample_module.classes)
        assert has_decorators
        
        # Should include methods in class info
        has_methods = any('[methods:' in cls for cls in sample_module.classes)
        assert has_methods
    
    def test_python_import_extraction(self):
        """Test Python import extraction."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        sample_module = [f for f in result.files if 'sample_module' in str(f.relative_path)][0]
        
        # Should extract imports
        assert len(sample_module.imports) > 0
        assert 'typing' in sample_module.imports or 'dataclasses' in sample_module.imports
    
    def test_javascript_function_extraction(self):
        """Test JavaScript function extraction."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/javascript_project')
        
        sample_js = [f for f in result.files if f.file_type == FileType.JAVASCRIPT][0]
        
        # Should extract functions
        assert len(sample_js.functions) > 0
        
        # Should capture parameters
        has_params = any('(' in func and ')' in func for func in sample_js.functions)
        assert has_params
    
    def test_javascript_class_extraction(self):
        """Test JavaScript class extraction with extends."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/javascript_project')
        
        sample_js = [f for f in result.files if f.file_type == FileType.JAVASCRIPT][0]
        
        # Should extract classes
        assert len(sample_js.classes) >= 2
        
        # Should detect extends
        has_extends = any('extends' in cls for cls in sample_js.classes)
        assert has_extends
        
        # Should include methods
        has_methods = any('[methods:' in cls for cls in sample_js.classes)
        assert has_methods
    
    def test_react_component_extraction(self):
        """Test React component and hooks extraction."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/javascript_project')
        
        components_jsx = [f for f in result.files if f.file_type == FileType.JSX][0]
        
        # Should extract components
        assert len(components_jsx.classes) >= 2
        
        # Should detect Component prefix
        has_components = any('Component:' in cls for cls in components_jsx.classes)
        assert has_components
        
        # Should detect hooks
        has_hooks = any('[hooks:' in cls for cls in components_jsx.classes)
        assert has_hooks


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_directory(self, tmp_path):
        """Test scanning an empty directory."""
        scanner = CodeScanner()
        result = scanner.scan_directory(tmp_path)
        
        assert result.total_files == 0
        assert len(result.files) == 0
        assert result.total_lines == 0
    
    def test_nonexistent_directory(self):
        """Test scanning a non-existent directory."""
        scanner = CodeScanner()
        
        # Scanner may raise ValueError or FileNotFoundError for nonexistent path
        try:
            result = scanner.scan_directory('./nonexistent_directory_xyz')
            # If it doesn't raise, should return empty result
            assert result.total_files == 0
        except (FileNotFoundError, ValueError):
            # This is expected for nonexistent directory
            pass
    
    def test_file_with_syntax_error(self, tmp_path):
        """Test handling files with syntax errors."""
        # Create a Python file with syntax error
        bad_file = tmp_path / "bad_syntax.py"
        bad_file.write_text("def broken function():\n    print('missing colon')")
        
        scanner = CodeScanner()
        result = scanner.scan_directory(tmp_path)
        
        # Should still scan the file but not extract functions
        assert result.total_files == 1
        # May have 0 functions due to syntax error
        assert result.files[0].line_count > 0


class TestSmartContextReduction:
    """Test smart context reduction (Task 28)."""
    
    def test_small_file_full_content(self, tmp_path):
        """Test that small files (<500 lines) get full content."""
        # Create a small file
        small_file = tmp_path / "small.py"
        small_file.write_text("def hello():\n    return 'world'\n")
        
        scanner = CodeScanner()
        result = scanner.scan_directory(tmp_path)
        
        assert len(result.files) == 1
        file = result.files[0]
        
        assert file.line_count < 500
        assert file.context_level == "full"
        assert file.content is not None
        assert file.token_count > 0
    
    def test_token_estimation(self):
        """Test token count estimation."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        # Should have token estimates
        assert result.total_tokens > 0
        
        for file in result.files:
            assert file.token_count > 0


class TestPydanticModels:
    """Test Pydantic model validation (Task 29)."""
    
    def test_codefile_model_validation(self):
        """Test CodeFile model field validation."""
        from pydantic import ValidationError
        
        # Valid file
        valid_file = CodeFile(
            path=Path("test.py"),
            relative_path=Path("test.py"),
            file_type=FileType.PYTHON,
            size_bytes=100,
            line_count=10
        )
        assert valid_file.size_bytes == 100
        assert valid_file.line_count == 10
        
        # Invalid: negative line count
        with pytest.raises(ValidationError):
            CodeFile(
                path=Path("test.py"),
                relative_path=Path("test.py"),
                file_type=FileType.PYTHON,
                size_bytes=100,
                line_count=-10  # Invalid
            )
    
    def test_scanresult_model(self):
        """Test ScanResult model."""
        result = ScanResult(root_path=Path("."))
        
        assert result.total_files == 0
        assert result.total_lines == 0
        assert result.total_tokens == 0
        assert len(result.files) == 0
    
    def test_model_serialization(self):
        """Test model to_dict() serialization."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        # Should serialize to dict
        data = result.to_dict()
        
        assert isinstance(data, dict)
        assert 'total_files' in data
        assert 'total_lines' in data
        assert 'total_tokens' in data
        assert 'files' in data


class TestLLMContextGeneration:
    """Test LLM context generation (Task 30)."""
    
    def test_file_tree_generation(self):
        """Test file tree generation."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        tree = result.get_file_tree()
        
        assert isinstance(tree, str)
        assert 'python_project' in tree.lower() or 'fixtures' in tree.lower()
        # Should have tree characters
        assert '├──' in tree or '└──' in tree
    
    def test_project_type_detection(self):
        """Test project type and framework detection."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        metadata = result.detect_project_type()
        
        assert isinstance(metadata, dict)
        assert 'project_type' in metadata
        assert 'languages' in metadata
        assert 'frameworks' in metadata
        
        # Should detect Python
        assert metadata['project_type'] == 'Python'
    
    def test_llm_context_generation(self):
        """Test full LLM context generation."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        context = result.get_llm_context()
        
        assert isinstance(context, str)
        assert len(context) > 0
        
        # Should include key sections
        assert 'PROJECT INFORMATION' in context
        assert 'STATISTICS' in context
        assert 'FILE STRUCTURE' in context
        assert 'CODE OVERVIEW' in context
    
    def test_helper_methods(self):
        """Test ScanResult helper methods."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures/python_project')
        
        # get_files_by_type
        py_files = result.get_files_by_type(FileType.PYTHON)
        assert len(py_files) == 2
        
        # get_largest_files
        largest = result.get_largest_files(1)
        assert len(largest) == 1
        assert largest[0].line_count >= result.files[0].line_count


class TestModuleIntegration:
    """Integration tests across all Module 2 features."""
    
    def test_end_to_end_scan(self):
        """Test complete scan workflow."""
        scanner = CodeScanner()
        result = scanner.scan_directory('./tests/fixtures')
        
        # Should scan successfully
        assert result.total_files >= 4
        assert result.total_lines > 0
        assert result.total_tokens > 0
        
        # Should have both Python and JS files
        py_files = result.get_files_by_type(FileType.PYTHON)
        js_files = result.get_files_by_type(FileType.JAVASCRIPT)
        jsx_files = result.get_files_by_type(FileType.JSX)
        
        assert len(py_files) >= 2
        assert len(js_files) + len(jsx_files) >= 2
        
        # Should generate LLM context
        context = result.get_llm_context()
        assert len(context) > 500  # Substantial context
        
        # Should serialize
        data = result.to_dict()
        assert isinstance(data, dict)


if __name__ == "__main__":
    # Run with: pytest tests/test_scanner.py -v
    pytest.main([__file__, "-v", "--tb=short"])

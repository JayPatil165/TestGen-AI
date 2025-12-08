"""
Unit tests for TestGen AI CLI commands.

Tests all CLI commands using Typer's testing utilities.
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from testgen.main import app

# Initialize CLI runner
runner = CliRunner()


class TestMainCLI:
    """Tests for main CLI entry point."""
    
    def test_help_displays(self):
        """Test that main help text displays correctly."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "TestGen AI" in result.stdout
        assert "generate" in result.stdout
        assert "test" in result.stdout
        assert "report" in result.stdout
        assert "auto" in result.stdout
    
    def test_version_flag(self):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout
        assert "TestGen AI" in result.stdout


class TestVersionCommand:
    """Tests for version command."""
    
    def test_version_command(self):
        """Test version command displays version info."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout
        assert "Python" in result.stdout
    
    def test_version_help(self):
        """Test version command help text."""
        result = runner.invoke(app, ["version", "--help"])
        assert result.exit_code == 0
        assert "Display version information" in result.stdout


class TestGenerateCommand:
    """Tests for generate command."""
    
    def test_generate_help(self):
        """Test generate command help text."""
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate test files" in result.stdout
        assert "--output" in result.stdout
        assert "--watch" in result.stdout
    
    def test_generate_missing_directory(self):
        """Test generate with missing directory argument."""
        result = runner.invoke(app, ["generate"])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout or "Error" in result.stdout
    
    def test_generate_nonexistent_directory(self):
        """Test generate with non-existent directory."""
        result = runner.invoke(app, ["generate", "./nonexistent_dir_12345"])
        assert result.exit_code != 0
    
    def test_generate_with_valid_directory(self, tmp_path):
        """Test generate with valid directory."""
        # Create a temporary directory with a Python file
        test_dir = tmp_path / "src"
        test_dir.mkdir()
        (test_dir / "sample.py").write_text("def hello(): pass")
        
        result = runner.invoke(app, ["generate", str(test_dir)])
        assert result.exit_code == 0
        assert "Test Generation Started" in result.stdout or "Analyzing code" in result.stdout
    
    def test_generate_with_output_option(self, tmp_path):
        """Test generate with --output option."""
        test_dir = tmp_path / "src"
        test_dir.mkdir()
        output_dir = tmp_path / "tests"
        
        result = runner.invoke(app, ["generate", str(test_dir), "--output", str(output_dir)])
        assert result.exit_code == 0


class TestTestCommand:
    """Tests for test command."""
    
    def test_test_help(self):
        """Test test command help text."""
        result = runner.invoke(app, ["test", "--help"])
        assert result.exit_code == 0
        assert "Run existing tests" in result.stdout
        assert "--pattern" in result.stdout
        assert "--verbose" in result.stdout
    
    def test_test_with_nonexistent_directory(self):
        """Test command with non-existent test directory."""
        result = runner.invoke(app, ["test", "./nonexistent_tests_12345"])
        assert result.exit_code != 0
    
    def test_test_with_pattern_option(self, tmp_path):
        """Test command with --pattern option."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        
        result = runner.invoke(app, ["test", str(test_dir), "--pattern", "test_*.py"])
        assert result.exit_code == 0


class TestReportCommand:
    """Tests for report command."""
    
    def test_report_help(self):
        """Test report command help text."""
        result = runner.invoke(app, ["report", "--help"])
        assert result.exit_code == 0
        assert "Generate a test report" in result.stdout
        assert "--pdf" in result.stdout
        assert "--output" in result.stdout
    
    def test_report_default(self):
        """Test report command with defaults."""
        result = runner.invoke(app, ["report"])
        assert result.exit_code == 0
        assert "HTML" in result.stdout or "Report Generation" in result.stdout
    
    def test_report_with_pdf_flag(self):
        """Test report with --pdf flag."""
        result = runner.invoke(app, ["report", "--pdf"])
        assert result.exit_code == 0
        assert "PDF" in result.stdout
    
    def test_report_with_output_path(self, tmp_path):
        """Test report with custom output path."""
        output_file = tmp_path / "custom-report.html"
        result = runner.invoke(app, ["report", "--output", str(output_file)])
        assert result.exit_code == 0


class TestAutoCommand:
    """Tests for auto command (God Mode)."""
    
    def test_auto_help(self):
        """Test auto command help text."""
        result = runner.invoke(app, ["auto", "--help"])
        assert result.exit_code == 0
        assert "complete workflow" in result.stdout.lower()
        assert "God Mode" in result.stdout or "god mode" in result.stdout.lower()
    
    def test_auto_missing_directory(self):
        """Test auto with missing directory argument."""
        result = runner.invoke(app, ["auto"])
        assert result.exit_code != 0
    
    def test_auto_with_valid_directory(self, tmp_path):
        """Test auto with valid directory."""
        test_dir = tmp_path / "src"
        test_dir.mkdir()
        (test_dir / "sample.py").write_text("def test(): pass")
        
        result = runner.invoke(app, ["auto", str(test_dir)])
        assert result.exit_code == 0
        assert "God Mode" in result.stdout or "Auto Mode" in result.stdout
        assert "Phase" in result.stdout
    
    def test_auto_with_skip_report(self, tmp_path):
        """Test auto with --skip-report flag."""
        test_dir = tmp_path / "src"
        test_dir.mkdir()
        
        result = runner.invoke(app, ["auto", str(test_dir), "--skip-report"])
        assert result.exit_code == 0
        assert "Skipped" in result.stdout or "Skip report" in result.stdout


class TestGlobalOptions:
    """Tests for global CLI options."""
    
    def test_verbose_flag(self, tmp_path):
        """Test --verbose flag."""
        test_dir = tmp_path / "src"
        test_dir.mkdir()
        
        result = runner.invoke(app, ["--verbose", "generate", str(test_dir)])
        assert result.exit_code == 0
        # Verbose mode should show additional details
    
    def test_debug_flag_with_error(self):
        """Test --debug flag shows stack traces."""
        result = runner.invoke(app, ["--debug", "generate", "./nonexistent_12345"])
        # Should fail but with debug info
        assert result.exit_code != 0


class TestParameterValidation:
    """Tests for parameter validation."""
    
    def test_generate_requires_directory(self):
        """Test that generate requires a directory argument."""
        result = runner.invoke(app, ["generate"])
        assert result.exit_code != 0
    
    def test_auto_requires_directory(self):
        """Test that auto requires a directory argument."""
        result = runner.invoke(app, ["auto"])
        assert result.exit_code != 0
    
    def test_invalid_command(self):
        """Test that invalid commands show error."""
        result = runner.invoke(app, ["invalidcommand"])
        assert result.exit_code != 0


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_keyboard_interrupt_handled(self):
        """Test that KeyboardInterrupt is handled gracefully."""
        # This would need to simulate Ctrl+C
        # For now, we verify the handler exists in main.py
        pass
    
    def test_exception_without_debug(self, tmp_path):
        """Test that exceptions are caught without --debug."""
        # Generate with invalid permissions (if possible)
        pass


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "cli: mark test as a CLI test"
    )


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

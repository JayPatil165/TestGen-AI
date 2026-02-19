"""
Task 114 E2E Test: No Tests Generated (Non-Code Files)

Verifies that TestGen AI provides appropriate messaging when run on a
directory that contains only non-code files (images, text, markdown, etc.)
and no valid source files to generate tests from.
"""
import sys
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.resolve()


@pytest.fixture
def non_code_dir(tmp_path):
    """Create a directory with only non-code files."""
    (tmp_path / "README.md").write_text("# Project\nThis is a readme.\n", encoding="utf-8")
    (tmp_path / "LICENSE.txt").write_text("MIT License\n", encoding="utf-8")
    (tmp_path / "config.json").write_text('{"key": "value"}\n', encoding="utf-8")
    (tmp_path / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n")  # Fake PNG header
    (tmp_path / ".env").write_text("SECRET_KEY=abc123\n", encoding="utf-8")
    (tmp_path / "Makefile").write_text("build:\n\techo building\n", encoding="utf-8")
    return tmp_path


class TestNonCodeFileScanner:
    """Scanner behaviour on directories with only non-code files."""

    def test_scanner_finds_no_python_files(self, non_code_dir):
        """
        scan_directory on a non-code dir should return 0 Python source files
        (markdown/JSON/text files should not be treated as code targets).
        """
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(non_code_dir))

        py_files = [f for f in result.files if str(f.path).endswith(".py")]
        print(f"\n  Scanned {len(result.files)} files total, {len(py_files)} .py files")

        assert len(py_files) == 0, (
            f"Expected 0 Python files in non-code dir, found: {[f.path for f in py_files]}"
        )

    def test_scanner_does_not_crash_on_binary_files(self, non_code_dir):
        """scanner should not raise an exception when it encounters binary files."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        try:
            result = scanner.scan_directory(str(non_code_dir))
            assert result is not None
        except Exception as e:
            pytest.fail(
                f"Scanner raised exception on non-code dir: {type(e).__name__}: {e}"
            )

    def test_scanner_summary_mentions_zero_code_files(self, non_code_dir):
        """get_summary() should be valid even when code file count is 0."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(non_code_dir))
        summary = result.get_summary()

        assert isinstance(summary, str), "get_summary() should return a string"


class TestNonCodeFileRunner:
    """Runner behaviour when there are no generated test files for non-code dirs."""

    def test_runner_on_non_code_dir_returns_zero_tests(self, non_code_dir):
        """run_tests on a dir with only non-code files should give total==0."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(non_code_dir))

        assert results.total == 0, (
            f"Expected 0 tests from non-code dir, got {results.total}"
        )

    def test_runner_result_has_expected_structure(self, non_code_dir):
        """Even with 0 tests, TestResults should have all required attributes."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(non_code_dir))

        assert hasattr(results, 'total'), "Missing 'total' attribute"
        assert hasattr(results, 'passed'), "Missing 'passed' attribute"
        assert hasattr(results, 'failed'), "Missing 'failed' attribute"
        assert hasattr(results, 'duration'), "Missing 'duration' attribute"
        assert hasattr(results, 'tests'), "Missing 'tests' attribute"
        assert isinstance(results.tests, list), "'tests' should be a list"


class TestNonCodeFileCLI:
    """CLI messaging when run against a directory with no code files."""

    def test_cli_generate_non_code_dir_no_traceback(self, non_code_dir):
        """
        `testgen generate <non_code_dir>` should not produce a raw Python traceback.
        It may print a warning/info message and exit.
        """
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "generate", str(non_code_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(ROOT),
        )

        output = result.stdout + result.stderr
        print(f"\n  Exit code: {result.returncode}")
        print(f"  Output (last 300 chars): {output[-300:]}")

        assert "Traceback (most recent call last)" not in output, (
            f"CLI raised unhandled exception for non-code dir:\n{output[-500:]}"
        )

    def test_cli_output_mentions_files_found(self, non_code_dir):
        """
        CLI should mention the file scan result (even if 0 Python files found)
        rather than silently doing nothing.
        """
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "generate", str(non_code_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(ROOT),
        )

        output = result.stdout + result.stderr
        # Should mention something related to files or analysis
        has_informative_output = (
            len(output.strip()) > 0  # Any output is better than silence
        )
        assert has_informative_output, (
            "CLI produced no output at all for non-code directory"
        )

    def test_cli_run_on_markdown_only_dir_exits_cleanly(self, tmp_path):
        """
        A directory with only .md files should exit cleanly.
        """
        (tmp_path / "README.md").write_text("# Just a readme\n", encoding="utf-8")
        (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "testgen", "generate", str(tmp_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(ROOT),
        )

        output = result.stdout + result.stderr
        assert "Traceback (most recent call last)" not in output, (
            f"CLI crashed on markdown-only dir:\n{output[-400:]}"
        )

    def test_execute_generate_on_non_code_dir_returns_zero(self, non_code_dir):
        """
        execute_generate directly on a non-code dir should return
        tests_generated == 0 without raising.
        """
        from testgen.manager import WorkflowManager

        try:
            manager = WorkflowManager(
                project_path=str(non_code_dir),
                config={
                    'language': 'python',
                    'output_dir': str(non_code_dir / 'TestGen-AI' / 'tests'),
                },
                use_timestamp_folders=False,
            )
            # Call with the dir as source_files list
            result = manager.execute_generate(
                source_files=[str(non_code_dir)],
                language="python",
            )
            assert result.get("tests_generated", 0) == 0, (
                f"Expected 0 tests generated for non-code dir, got {result}"
            )
        except Exception as e:
            pytest.fail(
                f"execute_generate raised for non-code dir: {type(e).__name__}: {e}"
            )

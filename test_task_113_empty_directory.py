"""
Task 113 E2E Test: Empty Directory Handling

Verifies that TestGen AI handles empty directories gracefully:
  - Scanner reports 0 files without crashing
  - Manager/runner show appropriate messaging
  - CLI exits with informative output (not a traceback)
"""
import sys
import subprocess
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.resolve()


class TestEmptyDirectoryScanner:
    """CodeScanner behaviour on an empty directory."""

    def test_scanner_returns_empty_result_for_empty_dir(self, tmp_path):
        """scan_directory on an empty folder returns ScanResult with 0 files."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))

        assert result is not None, "scan_directory should return a ScanResult, not None"
        assert len(result.files) == 0, (
            f"Expected 0 files for empty dir, got {len(result.files)}"
        )

    def test_scanner_empty_dir_total_lines_zero(self, tmp_path):
        """ScanResult.total_lines and total_tokens should be 0 for empty dir."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))

        assert result.total_lines == 0, (
            f"Expected total_lines==0 for empty dir, got {result.total_lines}"
        )
        assert result.total_tokens == 0, (
            f"Expected total_tokens==0 for empty dir, got {result.total_tokens}"
        )

    def test_scanner_empty_dir_summary_is_string(self, tmp_path):
        """get_summary() should return a non-crashing string even for empty dirs."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))
        summary = result.get_summary()

        assert isinstance(summary, str), "get_summary() should return a string"

    def test_scanner_handles_nonexistent_dir_gracefully(self, tmp_path):
        """Scanning a non-existent directory should not raise an unhandled exception."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        nonexistent = tmp_path / "does_not_exist"

        try:
            result = scanner.scan_directory(str(nonexistent))
            # If it returns, result should be empty/safe
            assert result is not None
        except (FileNotFoundError, OSError, ValueError):
            # Acceptable — a clear, typed exception is fine (scanner raises ValueError)
            pass
        except Exception as e:
            pytest.fail(
                f"scanner raised unexpected exception for nonexistent dir: {type(e).__name__}: {e}"
            )



class TestEmptyDirectoryRunner:
    """PythonTestRunner behaviour when there are no test files."""

    def test_runner_returns_zero_total_for_empty_dir(self, tmp_path):
        """run_tests on a dir with no test files should return total==0."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(tmp_path))

        assert results is not None, "run_tests should return a TestResults object"
        assert results.total == 0, (
            f"Expected total==0 for empty test dir, got {results.total}"
        )

    def test_runner_does_not_crash_for_nonexistent_dir(self, tmp_path):
        """run_tests on a non-existent directory should return safely with zero results."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        nonexistent = tmp_path / "no_tests_here"
        results = runner.run_tests(test_dir=str(nonexistent))

        assert results is not None
        assert results.total == 0


class TestEmptyDirectoryCLI:
    """CLI graceful handling of empty / missing directories."""

    def test_cli_generate_on_empty_dir_exits_cleanly(self, tmp_path):
        """
        `testgen generate <empty_dir>` should exit without crashing.
        It may fail (non-zero exit) due to no files found, but must not produce
        a raw Python traceback.
        """
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
        print(f"\n  Exit code: {result.returncode}")
        print(f"  Output (last 300 chars): {output[-300:]}")

        # Must not produce an unhandled Python traceback
        assert "Traceback (most recent call last)" not in output, (
            f"CLI raised an unhandled exception for empty dir:\n{output[-500:]}"
        )

    def test_cli_generate_on_nonexistent_dir_exits_with_error(self, tmp_path):
        """
        `testgen generate <nonexistent>` should exit with a non-zero code
        and an informative message, not a raw traceback.
        """
        fake = tmp_path / "doesnt_exist_at_all"
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "generate", str(fake)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(ROOT),
        )

        output = result.stdout + result.stderr
        print(f"\n  Exit code: {result.returncode}")
        print(f"  Output: {output[-300:]}")

        assert result.returncode != 0 or "not found" in output.lower() or "error" in output.lower(), (
            "Expected non-zero exit or error message for nonexistent directory"
        )
        assert "Traceback (most recent call last)" not in output, (
            f"CLI showed raw traceback for nonexistent dir:\n{output[-500:]}"
        )

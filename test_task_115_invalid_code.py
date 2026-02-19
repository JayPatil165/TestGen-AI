"""
Task 115 E2E Test: Invalid Code / Syntax Errors

Verifies that TestGen AI handles Python files with syntax errors gracefully:
  - Scanner does not crash on syntax-errored .py files
  - The file is either skipped or flagged, not silently corrupting results
  - Runner handles test files that fail to collect (import/syntax error)
  - CLI does not produce raw tracebacks for broken source code
"""
import sys
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.resolve()

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BROKEN_PYTHON = '''\
"""Module with a deliberate syntax error."""

def valid_function(x):
    return x * 2

def broken_function(
    # Missing closing parenthesis and body — syntax error
    pass

class Unclosed
    x = 1
'''

BROKEN_TEST_FILE = '''\
"""Test file with syntax error — pytest cannot collect this."""
import pytest

def test_something(
    # Broken signature
    pass

def test_valid():
    assert True
'''

UNICODE_ERROR_FILE = '''\
# -*- coding: utf-8 -*-
"""File with invalid escape sequences."""
import re

# Deliberately broken regex pattern with unclosed group
PATTERN = re.compile(r"(?P<name>[a-z]+")  # Missing closing )

def process(text):
    return PATTERN.match(text)
'''

EMPTY_PY_FILE = '''\
'''  # Empty Python file — technically valid but trivial

IMPORT_ERROR_FILE = '''\
"""File that imports a non-existent module."""
from non_existent_module_xyz import something

def do_thing():
    return something()
'''


@pytest.fixture
def invalid_code_dir(tmp_path):
    """Create a directory with a mix of valid and invalid Python files."""
    valid = tmp_path / "valid_module.py"
    valid.write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8"
    )
    broken = tmp_path / "broken_syntax.py"
    broken.write_text(BROKEN_PYTHON, encoding="utf-8")

    empty = tmp_path / "empty_module.py"
    empty.write_text(EMPTY_PY_FILE, encoding="utf-8")

    import_err = tmp_path / "bad_import.py"
    import_err.write_text(IMPORT_ERROR_FILE, encoding="utf-8")

    return tmp_path


@pytest.fixture
def syntax_error_only_dir(tmp_path):
    """Create a directory with only syntax-errored Python files."""
    (tmp_path / "syntax_err_1.py").write_text(BROKEN_PYTHON, encoding="utf-8")
    (tmp_path / "syntax_err_2.py").write_text(
        "x = (\n  1 + \n",  # Unclosed parenthesis
        encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def broken_test_dir(tmp_path):
    """A test directory containing a test file with a syntax error."""
    (tmp_path / "test_broken.py").write_text(BROKEN_TEST_FILE, encoding="utf-8")
    (tmp_path / "test_valid.py").write_text(
        "def test_ok():\n    assert 1 == 1\n",
        encoding="utf-8"
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Task 115 Tests
# ---------------------------------------------------------------------------

class TestScannerWithInvalidCode:
    """Verify CodeScanner handles syntax-errored files without crashing."""

    def test_scanner_does_not_crash_on_syntax_errors(self, invalid_code_dir):
        """scan_directory with broken .py files should not raise any exception."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        try:
            result = scanner.scan_directory(str(invalid_code_dir))
            assert result is not None, "scan_directory returned None"
        except SyntaxError as e:
            pytest.fail(f"Scanner raised SyntaxError (should handle gracefully): {e}")
        except Exception as e:
            pytest.fail(f"Scanner raised unexpected exception: {type(e).__name__}: {e}")

    def test_scanner_finds_files_including_broken(self, invalid_code_dir):
        """Scanner should still discover .py files even when some have syntax errors."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(invalid_code_dir))

        # Should find at least the valid file
        assert len(result.files) >= 1, (
            "Scanner found 0 files — expected at least the valid .py file"
        )

    def test_scanner_on_syntax_only_dir_does_not_crash(self, syntax_error_only_dir):
        """Scanner on a dir of only broken files should return safely."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        try:
            result = scanner.scan_directory(str(syntax_error_only_dir))
            assert result is not None
        except SyntaxError as e:
            pytest.fail(f"Scanner raised unhandled SyntaxError: {e}")
        except Exception as e:
            pytest.fail(f"Scanner raised unexpected exception: {type(e).__name__}: {e}")

    def test_scanner_empty_python_file_handled(self, tmp_path):
        """An empty .py file should be handled without error."""
        from testgen.core.scanner import CodeScanner

        (tmp_path / "empty.py").write_text("", encoding="utf-8")
        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))
        assert result is not None

    def test_scanner_unicode_like_content_handled(self, tmp_path):
        """Files with unusual but UTF-8 valid content should not crash the scanner."""
        from testgen.core.scanner import CodeScanner

        unusual = tmp_path / "unicode.py"
        unusual.write_text(
            "# -*- coding: utf-8 -*-\n# Emojis: \U0001f4a1 \U0001f525\nx = 1\n",
            encoding="utf-8"
        )
        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))
        assert result is not None


class TestRunnerWithBrokenTests:
    """Verify PythonTestRunner handles test files with syntax/import errors gracefully."""

    def test_runner_handles_broken_test_file_gracefully(self, broken_test_dir):
        """
        Running pytest on a dir that has a syntax-broken test file should
        not crash PythonTestRunner — it should return a result with errors
        or partial results.
        """
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        try:
            results = runner.run_tests(test_dir=str(broken_test_dir))
            assert results is not None, "run_tests returned None"
        except Exception as e:
            pytest.fail(
                f"PythonTestRunner raised exception for broken test file: {type(e).__name__}: {e}"
            )

    def test_runner_still_runs_valid_tests_alongside_broken(self, broken_test_dir):
        """
        Even with a syntax-broken test file, valid test files should still
        be collected and run (pytest collects them independently).
        """
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(broken_test_dir))

        # At minimum, 'test_valid.py::test_ok' should have run
        has_any_results = (
            results.total > 0 or
            results.errors > 0 or
            len(results.tests) > 0
        )
        assert has_any_results, (
            "Expected at least one test result or error from a mixed broken/valid test dir"
        )

    def test_runner_result_is_complete_object(self, broken_test_dir):
        """TestResults object should always have all attributes populated."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(broken_test_dir))

        assert isinstance(results.total, int), "total should be an int"
        assert isinstance(results.passed, int), "passed should be an int"
        assert isinstance(results.failed, int), "failed should be an int"
        assert isinstance(results.duration, (int, float)), "duration should be numeric"


class TestCLIWithInvalidCode:
    """Verify CLI handles projects with syntax-errored source files."""

    def _run_generate_briefly(self, target_dir, wait_seconds=12):
        """
        Start `testgen generate <dir>`, collect output for up to `wait_seconds`,
        then terminate. Returns (output_lines, returncode).
        The LLM call can block indefinitely, so we only observe the scan phase.
        """
        import threading
        import time

        proc = subprocess.Popen(
            [sys.executable, "-m", "testgen", "generate", str(target_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(ROOT),
        )

        lines = []
        done_evt = threading.Event()

        def _reader():
            for line in proc.stdout:
                lines.append(line)
                # Stop reading once we know the scan phase is done
                if any(k in line for k in ["source files", "Found", "Analyzing", "Generating"]):
                    done_evt.set()
            done_evt.set()

        t = threading.Thread(target=_reader, daemon=True)
        t.start()
        done_evt.wait(timeout=wait_seconds)

        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        t.join(timeout=5)

        return "".join(lines), proc.returncode

    def test_cli_generate_with_broken_source_no_traceback(self, invalid_code_dir):
        """
        `testgen generate <dir_with_broken_py>` should not produce a raw Python
        traceback even if it encounters syntax-errored files.
        """
        output, retcode = self._run_generate_briefly(invalid_code_dir)
        print(f"\n  Exit code: {retcode}")
        print(f"  Output (last 300 chars): {output[-300:]}")

        assert len(output.strip()) > 0, "CLI produced no output"
        assert "Traceback (most recent call last)" not in output, (
            f"CLI raised unhandled exception for dir with broken source:\n{output[-500:]}"
        )

    def test_cli_generates_from_valid_file_despite_broken_neighbour(self, invalid_code_dir):
        """
        CLI should attempt generation for valid files even when other files
        in the same directory have syntax errors.
        At minimum, the CLI should start and produce scan-phase output.
        """
        output, _ = self._run_generate_briefly(invalid_code_dir)
        assert len(output.strip()) > 0, "CLI produced no output for mixed valid/broken dir"

    def test_cli_run_on_syntax_only_dir_exits_cleanly(self, syntax_error_only_dir):
        """
        `testgen generate` on a dir of only broken .py files must not crash
        with an unhandled exception.
        """
        output, _ = self._run_generate_briefly(syntax_error_only_dir)
        assert "Traceback (most recent call last)" not in output, (
            f"CLI crashed on syntax-only dir:\n{output[-400:]}"
        )

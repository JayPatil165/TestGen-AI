"""
Task 116 E2E Test: Windows Platform Testing

Verifies that TestGen AI works correctly on Windows:
  - File paths use correct separators (or pathlib neutral handling)
  - CLI commands work without POSIX-only assumptions
  - Output directories are created with Windows-compatible names
  - Unicode/emoji console output doesn't crash
  - Temp paths with spaces are handled correctly
"""
import sys
import os
import subprocess
import platform
from pathlib import Path, PureWindowsPath, PurePosixPath

import pytest

ROOT = Path(__file__).parent.resolve()

# This test file is Windows-specific — always run on Windows, skip on others
IS_WINDOWS = platform.system() == "Windows"
pytestmark = pytest.mark.skipif(not IS_WINDOWS, reason="Windows-specific tests")


class TestWindowsPathHandling:
    """Verify that the tool handles Windows paths correctly."""

    def test_scanner_handles_windows_paths(self, tmp_path):
        """Scanner should work with Windows-style backslash paths."""
        from testgen.core.scanner import CodeScanner

        # Create a test file
        (tmp_path / "hello.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")

        scanner = CodeScanner()
        # Pass path using os.fspath (native format on Windows)
        result = scanner.scan_directory(os.fspath(tmp_path))
        assert result is not None
        assert len(result.files) >= 1

    def test_scanner_handles_path_with_spaces(self, tmp_path):
        """Scanner must work with directory names containing spaces."""
        from testgen.core.scanner import CodeScanner

        spaced_dir = tmp_path / "my project folder"
        spaced_dir.mkdir()
        (spaced_dir / "module.py").write_text("x = 42\n", encoding="utf-8")

        scanner = CodeScanner()
        result = scanner.scan_directory(str(spaced_dir))
        assert result is not None
        assert len(result.files) >= 1

    def test_scanner_handles_deep_nested_windows_path(self, tmp_path):
        """Scanner should not fail on deeply nested Windows paths."""
        from testgen.core.scanner import CodeScanner

        # Create 5 levels deep
        deep = tmp_path / "a" / "b" / "c" / "d" / "e"
        deep.mkdir(parents=True)
        (deep / "deep_module.py").write_text("def deep(): pass\n", encoding="utf-8")

        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))
        assert result is not None
        assert any("deep_module" in str(f.path) for f in result.files), (
            "Expected to find deep_module.py in nested path"
        )

    def test_scanner_file_paths_are_pathlib_compatible(self, tmp_path):
        """
        All file paths in ScanResult should be representable as pathlib.Path objects
        (no forward-slash only / POSIX strings that break windows open()).
        """
        from testgen.core.scanner import CodeScanner

        (tmp_path / "module.py").write_text("x = 1\n", encoding="utf-8")
        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))

        for f in result.files:
            path_obj = Path(f.path)
            assert path_obj.exists() or not path_obj.is_absolute(), (
                f"File path '{f.path}' should be a valid pathlib.Path"
            )

    def test_output_dir_created_with_windows_compatible_name(self, tmp_path):
        """
        WorkflowManager creates output directories with timestamp format.
        On Windows, colons in timestamps would break directory creation — verify safe naming.
        """
        from testgen.manager import WorkflowManager

        manager = WorkflowManager(
            project_path=str(tmp_path),
            use_timestamp_folders=True,
        )

        # Timestamp folders should NOT have colons (Windows disallows them in paths)
        out_str = str(manager.output_dir)
        assert ":" not in out_str.split("\\")[-1], (
            f"Output dir name contains colon (invalid on Windows): {out_str}"
        )
        assert manager.output_dir.exists(), "Output directory should have been created"


class TestWindowsCLICommands:
    """Verify CLI commands work correctly on Windows."""

    def test_cli_help_works_on_windows(self):
        """testgen --help should exit with code 0 on Windows."""
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        assert result.returncode == 0, f"--help failed: {result.stderr}"
        assert "testgen" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_cli_generate_help_on_windows(self):
        """testgen generate --help should work on Windows."""
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "generate", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        assert result.returncode == 0, f"generate --help failed: {result.stderr}"

    def test_cli_run_help_on_windows(self):
        "`testgen test --help` should work on Windows."
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "test", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        assert result.returncode == 0, f"test --help failed: {result.stderr}"

    def test_cli_report_help_on_windows(self):
        """testgen report --help should work on Windows."""
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "report", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        assert result.returncode == 0, f"report --help failed: {result.stderr}"

    def test_cli_scan_help_on_windows(self):
        "`testgen report --help` should work on Windows."
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "report", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        assert result.returncode == 0, f"report --help failed: {result.stderr}"

    def test_cli_generate_on_windows_with_backslash_path(self, tmp_path):
        """
        CLI should accept paths with backslashes (Windows native) without error.
        """
        (tmp_path / "my_module.py").write_text("def foo(): pass\n", encoding="utf-8")

        # Use native Windows path string (backslashes)
        win_path = str(tmp_path)  # pathlib gives OS-native separators

        result = subprocess.run(
            [sys.executable, "-m", "testgen", "scan", win_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        output = result.stdout + result.stderr
        assert "Traceback (most recent call last)" not in output, (
            f"CLI produced traceback for Windows path:\n{output[-400:]}"
        )


class TestWindowsFileWatcher:
    """Verify file watcher works on Windows (uses watchdog which supports ReadDirectoryChangesW)."""

    def test_watcher_starts_and_stops_on_windows(self, tmp_path):
        """UniversalFileWatcher should start and stop cleanly on Windows."""
        from testgen.core.watcher import UniversalFileWatcher

        watcher = UniversalFileWatcher(
            watch_paths=[str(tmp_path)],
            languages=["python"],
        )
        try:
            watcher.start()
            assert watcher.is_running(), "Watcher should be running after start()"
        finally:
            watcher.stop()
            assert not watcher.is_running(), "Watcher should be stopped after stop()"

    def test_watcher_detects_file_creation_on_windows(self, tmp_path):
        """Watcher should detect a new .py file created on Windows."""
        import threading
        import time
        from testgen.core.watcher import UniversalFileWatcher

        detected = threading.Event()
        detected_path = []

        def on_change(event):
            detected_path.append(str(event.path))
            detected.set()

        from testgen.core.language_config import Language
        watcher = UniversalFileWatcher(
            watch_paths=[str(tmp_path)],
            languages=[Language.PYTHON],
            debounce_seconds=0.0,
        )
        watcher.on_change(on_change)
        watcher.start()

        try:
            time.sleep(2.0)  # Windows: wait longer for watcher thread/observer
            (tmp_path / "new_module.py").write_text("x = 1\n", encoding="utf-8")
            
            # Use a slightly longer polling wait
            for _ in range(15):
                if detected.is_set():
                    break
                time.sleep(1.0)
            
            assert detected.is_set(), "Watcher did not detect file creation on Windows"
        finally:
            watcher.stop()


class TestWindowsEncoding:
    """Verify encoding-related behaviors on Windows (default CP1252 vs UTF-8)."""

    def test_scanner_reads_utf8_files_correctly(self, tmp_path):
        """Scanner should read UTF-8 Python files with non-ASCII identifiers."""
        from testgen.core.scanner import CodeScanner

        (tmp_path / "utf8_module.py").write_text(
            '# -*- coding: utf-8 -*-\n'
            'greeting = "Héllo Wörld"\n'
            'def grüss(): pass\n',
            encoding="utf-8"
        )
        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))
        assert result is not None
        assert len(result.files) >= 1

    def test_runner_output_encoding_safe(self, tmp_path):
        """Runner should handle UTF-8 test output without crashing on Windows."""
        from testgen.core.python_runner import PythonTestRunner

        test_file = tmp_path / "test_unicode.py"
        test_file.write_text(
            '# -*- coding: utf-8 -*-\n'
            'def test_unicode_in_assert():\n'
            '    msg = "Pàss: \u2713"\n'
            '    assert True, msg\n',
            encoding="utf-8"
        )

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(tmp_path))
        assert results is not None
        assert results.passed >= 1

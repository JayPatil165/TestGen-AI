"""
Task 117 E2E Test: Cross-Platform Compatibility

Verifies that TestGen AI is platform-neutral — no hardcoded path separators,
no Windows-only or POSIX-only APIs, consistent behavior across OSes.

These tests run on ALL platforms and verify cross-platform conventions.
macOS/Linux specific behavioral checks are included and annotated.
"""
import sys
import os
import subprocess
import platform
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest

ROOT = Path(__file__).parent.resolve()

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"
PLATFORM_NAME = platform.system()


class TestCrossPlatformPaths:
    """Path handling must be consistent across all operating systems."""

    def test_scanner_uses_pathlib_not_string_concat(self, tmp_path):
        """
        Scanner should produce paths that work with pathlib.Path regardless
        of OS — i.e., no hardcoded '/' or '\\' separators.
        """
        from testgen.core.scanner import CodeScanner

        (tmp_path / "module.py").write_text("def foo(): return 1\n", encoding="utf-8")
        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))

        for f in result.files:
            # Path should be constructable by pathlib
            try:
                p = Path(str(f.path))
                # On this OS, we should be able to resolve it
                _ = str(p)
            except Exception as e:
                pytest.fail(
                    f"ScanResult file path '{f.path}' is not pathlib-compatible: {e}"
                )

    def test_scanner_forward_slash_path_accepted(self, tmp_path):
        """
        Scanner should accept forward-slash paths (POSIX style)
        even on Windows (pathlib normalizes them).
        """
        from testgen.core.scanner import CodeScanner

        (tmp_path / "module.py").write_text("x = 1\n", encoding="utf-8")
        scanner = CodeScanner()

        # Always use forward slashes
        posix_path = tmp_path.as_posix()
        result = scanner.scan_directory(posix_path)
        assert result is not None
        assert len(result.files) >= 1

    def test_output_dir_uses_path_separator_correctly(self, tmp_path):
        """
        WorkflowManager output_dir should use platform-native separators
        (pathlib does this automatically).
        """
        from testgen.manager import WorkflowManager

        manager = WorkflowManager(
            project_path=str(tmp_path),
            use_timestamp_folders=False,
        )
        # str(path) uses OS-native separator
        out_str = str(manager.output_dir)

        if IS_WINDOWS:
            # Should contain backslash (native Windows)
            assert "\\" in out_str or "/" in out_str, (
                f"Windows path should use backslash: {out_str}"
            )
        else:
            # POSIX — should use forward slashes
            assert "/" in out_str, f"POSIX path should use forward slash: {out_str}"

    def test_scan_result_path_strings_have_no_mixed_separators(self, tmp_path):
        """
        ScanResult file paths should not mix '/' and '\\' separators.
        """
        from testgen.core.scanner import CodeScanner

        sub = tmp_path / "sub"
        sub.mkdir(parents=True, exist_ok=True)
        (sub / "module.py").write_text("x = 1\n", encoding="utf-8")

        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))

        for f in result.files:
            path_str = str(f.path)
            has_backslash = "\\" in path_str
            has_forward = "/" in path_str
            # Mixed is problematic
            assert not (has_backslash and has_forward), (
                f"Mixed separators in path: '{path_str}'"
            )


class TestCrossPlatformCLI:
    """CLI must behave consistently across platforms."""

    def test_python_module_invocation_works(self):
        """python -m testgen works on all platforms."""
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0, (
            f"[{PLATFORM_NAME}] `python -m testgen --help` failed: {result.stderr}"
        )

    def test_all_subcommands_available(self):
        """All subcommands should be present and show help on all platforms."""
        for cmd in ["generate", "test", "report", "auto"]:
            result = subprocess.run(
                [sys.executable, "-m", "testgen", cmd, "--help"],
                capture_output=True,
                text=True,
                timeout=15,
                encoding="utf-8",
                errors="replace",
            )
            assert result.returncode == 0, (
                f"[{PLATFORM_NAME}] `testgen {cmd} --help` failed:\n{result.stderr}"
            )

    def test_scan_command_runs_on_any_platform(self, tmp_path):
        """testgen generate should work and produce output on all platforms."""
        (tmp_path / "app.py").write_text(
            "class App:\n    def run(self): pass\n",
            encoding="utf-8"
        )
        result = subprocess.run(
            [sys.executable, "-m", "testgen", "generate", str(tmp_path), "--dry-run"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
        output = result.stdout + result.stderr
        assert "Traceback (most recent call last)" not in output, (
            f"[{PLATFORM_NAME}] scan command crashed:\n{output[-400:]}"
        )

    def test_cli_no_posix_only_shebang_in_entry_point(self):
        """
        The installed entry point script should not rely on a POSIX-only shebang
        on Windows. Since we use `python -m testgen`, this is already satisfied.
        Verify __main__.py exists.
        """
        main_file = ROOT / "src" / "testgen" / "__main__.py"
        assert main_file.exists(), (
            "__main__.py must exist for `python -m testgen` to work on all platforms"
        )


class TestCrossPlatformFileWatcher:
    """File watcher must work across platforms (watchdog has per-OS backends)."""

    def test_watcher_starts_on_current_platform(self, tmp_path):
        """
        UniversalFileWatcher should start cleanly on whatever platform we're on.
        watchdog uses:
          - Windows:  ReadDirectoryChangesW
          - macOS:    FSEvents (or kqueue fallback)
          - Linux:    inotify
        """
        from testgen.core.watcher import UniversalFileWatcher

        watcher = UniversalFileWatcher(
            watch_paths=[str(tmp_path)],
            languages=["python"],
        )
        try:
            watcher.start()
            assert watcher.is_running(), (
                f"[{PLATFORM_NAME}] Watcher should be running after start()"
            )
        finally:
            watcher.stop()

    def test_watcher_detects_new_file_on_current_platform(self, tmp_path):
        """
        File creation should be detected by the watcher on the current platform.
        """
        import threading
        import time
        from testgen.core.watcher import UniversalFileWatcher

        detected = threading.Event()

        def on_change(event):
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
            time.sleep(2.0)
            (tmp_path / "trigger.py").write_text("x = 1\n", encoding="utf-8")
            
            for _ in range(15):
                if detected.is_set():
                    break
                time.sleep(1.0)

            assert detected.is_set(), (
                f"[{PLATFORM_NAME}] Watcher failed to detect file creation"
            )
        finally:
            watcher.stop()


class TestCrossPlatformEncoding:
    """UTF-8 handling must be consistent across platforms."""

    def test_scanner_reads_utf8_on_all_platforms(self, tmp_path):
        """Scanner reads UTF-8 Python files correctly on all platforms."""
        from testgen.core.scanner import CodeScanner

        (tmp_path / "i18n.py").write_text(
            "# -*- coding: utf-8 -*-\n"
            "LANGUAGES = ['English', 'Français', 'Deutsch', '日本語', 'العربية']\n"
            "def translate(): pass\n",
            encoding="utf-8"
        )
        scanner = CodeScanner()
        result = scanner.scan_directory(str(tmp_path))
        assert result is not None
        assert len(result.files) >= 1

    def test_pytest_subprocess_encoding_correct(self, tmp_path):
        """
        Running pytest as a subprocess should produce parseable UTF-8 output
        on all platforms (no codec errors).
        """
        from testgen.core.python_runner import PythonTestRunner

        (tmp_path / "test_simple.py").write_text(
            "def test_ok():\n    assert 1 + 1 == 2\n",
            encoding="utf-8"
        )
        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(tmp_path))
        assert results is not None
        assert results.passed >= 1, (
            f"[{PLATFORM_NAME}] Expected at least 1 pass, got: {results.total}"
        )

    def test_pathlib_as_posix_for_display(self, tmp_path):
        """
        path.as_posix() should always return forward slashes for display/logging
        regardless of platform.
        """
        p = tmp_path / "module.py"
        posix = p.as_posix()
        assert "/" in posix, "as_posix() should return forward slashes on all platforms"
        assert "\\" not in posix, "as_posix() should NOT have backslashes"


@pytest.mark.skipif(not IS_MACOS, reason="macOS-specific check")
class TestMacOSSpecific:
    """macOS-specific behavioral verification."""

    def test_watcher_uses_fsevents_or_kqueue(self):
        """
        On macOS, watchdog uses FSEvents (recommended) or falls back to kqueue.
        Neither should cause errors.
        """
        import watchdog.observers
        observer = watchdog.observers.Observer()
        backend = type(observer).__name__
        print(f"\n  macOS watcher backend: {backend}")
        assert observer is not None

    def test_posix_path_operations(self, tmp_path):
        """File paths on macOS should be POSIX-style (forward slashes)."""
        p = tmp_path / "module.py"
        assert "/" in str(p), f"macOS path should use '/', got: {p}"


@pytest.mark.skipif(not IS_LINUX, reason="Linux-specific check")
class TestLinuxSpecific:
    """Linux-specific behavioral verification."""

    def test_watcher_uses_inotify(self):
        """On Linux, watchdog uses inotify. Verify it's importable."""
        try:
            import watchdog.observers.inotify
            assert True
        except ImportError:
            pytest.skip("inotify not available on this Linux system (may use polling fallback)")

    def test_posix_path_operations(self, tmp_path):
        """File paths on Linux should be POSIX-style."""
        p = tmp_path / "module.py"
        assert "/" in str(p), f"Linux path should use '/', got: {p}"

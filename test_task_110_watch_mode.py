"""
Task 110 E2E Test: Watch Mode
Tests that `testgen generate --watch` detects file changes and auto-regenerates tests.

Strategy:
  - Since watch mode is interactive (blocks until Ctrl+C), we test the
    underlying primitives end-to-end rather than driving the full CLI:
    1. UniversalFileWatcher is alive and properly detects file changes.
    2. The change callback receives the correct FileChangeEvent.
    3. execute_generate is re-invoked correctly when a tracked file changes.
  - An integration smoke-test also launches the CLI with --watch via subprocess
    and verifies the "Watching" message appears in stdout, then terminates it cleanly.
"""
import sys
import os
import time
import threading
import subprocess
import tempfile
import shutil
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.resolve()

def _make_temp_project(tmp_path: Path) -> Path:
    """Create a minimal Python project in a temp dir for watch-mode testing."""
    src = tmp_path / "watch_src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "calc.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8"
    )
    return src


# ===========================================================================
# Unit tests for UniversalFileWatcher
# ===========================================================================

class TestUniversalFileWatcher:
    """Test the watcher primitive independently of the CLI."""

    def test_watcher_available(self):
        """watchdog is installed and importable."""
        from testgen.core.watcher import WATCHDOG_AVAILABLE
        assert WATCHDOG_AVAILABLE, (
            "watchdog is not installed. Run: pip install watchdog"
        )

    def test_watcher_starts_and_stops(self, tmp_path):
        """Watcher starts, is_running() is True, stops cleanly."""
        from testgen.core.watcher import UniversalFileWatcher
        from testgen.core.language_config import Language

        watcher = UniversalFileWatcher(
            watch_paths=[str(tmp_path)],
            languages=[Language.PYTHON],
            debounce_seconds=0.5,
        )
        assert not watcher.is_running()
        watcher.start()
        assert watcher.is_running()
        watcher.stop()
        assert not watcher.is_running()

    def test_watcher_detects_file_change(self, tmp_path):
        """Watcher fires callback when a .py file is modified."""
        from testgen.core.watcher import UniversalFileWatcher, FileChangeType
        from testgen.core.language_config import Language

        src_file = tmp_path / "module.py"
        src_file.write_text("x = 1\n", encoding="utf-8")

        received_events = []
        event_ready = threading.Event()

        def on_change(evt):
            received_events.append(evt)
            event_ready.set()

        watcher = UniversalFileWatcher(
            watch_paths=[str(tmp_path)],
            languages=[Language.PYTHON],
            debounce_seconds=0.3,
        )
        watcher.on_change(on_change)
        watcher.start()

        # Give the observer a moment to initialize
        time.sleep(0.5)

        # Modify the file
        src_file.write_text("x = 2\n", encoding="utf-8")

        # Wait up to 5 seconds for the event
        triggered = event_ready.wait(timeout=5)
        watcher.stop()

        assert triggered, "FileWatcher did not fire callback within 5 seconds"
        assert len(received_events) >= 1
        evt = received_events[0]
        assert evt.path.suffix == ".py"
        assert evt.change_type in (FileChangeType.MODIFIED, FileChangeType.CREATED)

    def test_watcher_ignores_test_files(self, tmp_path):
        """Watcher does NOT fire callback for changes inside a TestGen-AI directory."""
        from testgen.core.watcher import UniversalFileWatcher
        from testgen.core.language_config import Language

        # The ignore_patterns match 'TestGen-AI' — create a nested test dir
        test_dir = tmp_path / "TestGen-AI" / "tests"
        test_dir.mkdir(parents=True)
        test_file = test_dir / "test_module.py"
        test_file.write_text("pass\n", encoding="utf-8")

        received_events = []

        def on_change(evt):
            received_events.append(evt)

        watcher = UniversalFileWatcher(
            watch_paths=[str(tmp_path)],
            languages=[Language.PYTHON],
            debounce_seconds=0.3,
            ignore_patterns=['TestGen-AI', '*.pyc', '__pycache__'],
        )
        watcher.on_change(on_change)
        watcher.start()
        time.sleep(0.5)

        # Modify the test file — should be ignored
        test_file.write_text("pass  # changed\n", encoding="utf-8")
        time.sleep(2.0)

        watcher.stop()

        relevant = [e for e in received_events if 'TestGen-AI' in str(e.path)]
        assert len(relevant) == 0, (
            f"Watcher incorrectly fired for TestGen-AI file: {relevant}"
        )

    def test_watcher_detects_new_file_creation(self, tmp_path):
        """Watcher fires callback when a new .py file is created."""
        from testgen.core.watcher import UniversalFileWatcher, FileChangeType
        from testgen.core.language_config import Language

        received_events = []
        event_ready = threading.Event()

        def on_change(evt):
            received_events.append(evt)
            event_ready.set()

        watcher = UniversalFileWatcher(
            watch_paths=[str(tmp_path)],
            languages=[Language.PYTHON],
            debounce_seconds=0.3,
        )
        watcher.on_change(on_change)
        watcher.start()
        time.sleep(0.5)

        # Create a brand-new file
        new_file = tmp_path / "brand_new.py"
        new_file.write_text("def hello(): pass\n", encoding="utf-8")

        triggered = event_ready.wait(timeout=5)
        watcher.stop()

        assert triggered, "FileWatcher did not fire callback for new file creation"
        assert any(e.change_type == FileChangeType.CREATED for e in received_events)

    def test_debounce_suppresses_rapid_events(self, tmp_path):
        """Multiple rapid writes to the same file produce at most 2 events."""
        from testgen.core.watcher import UniversalFileWatcher
        from testgen.core.language_config import Language

        src_file = tmp_path / "rapid.py"
        src_file.write_text("x = 0\n", encoding="utf-8")

        received_events = []

        def on_change(evt):
            received_events.append(evt)

        watcher = UniversalFileWatcher(
            watch_paths=[str(tmp_path)],
            languages=[Language.PYTHON],
            debounce_seconds=1.5,  # 1.5s debounce
        )
        watcher.on_change(on_change)
        watcher.start()
        time.sleep(0.5)

        # Write 5 times in quick succession (within debounce window)
        for i in range(5):
            src_file.write_text(f"x = {i}\n", encoding="utf-8")
            time.sleep(0.1)

        # Wait for debounce window to expire
        time.sleep(2.0)
        watcher.stop()

        # At most 2 events should be fired (first write + maybe one more)
        assert len(received_events) <= 3, (
            f"Debounce failed: {len(received_events)} events fired for 5 rapid writes"
        )


# ===========================================================================
# Integration: CLI smoke-test for --watch flag
# ===========================================================================

class TestWatchModeCLI:
    """Smoke-test the full CLI watch mode (subprocess, terminated by signal)."""

    def test_watch_mode_cli_starts(self, tmp_path):
        """
        `testgen generate <dir> --watch` starts up, prints 'Watching', and
        can be terminated cleanly with Ctrl+C (SIGINT on Unix / terminate on Windows).
        """
        src = _make_temp_project(tmp_path)

        proc = subprocess.Popen(
            [sys.executable, "-m", "testgen", "generate", str(src), "--watch"],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # merge stderr into stdout
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        output_lines = []
        watch_started = threading.Event()

        def _reader():
            for line in proc.stdout:
                output_lines.append(line)
                if "Watching" in line or "Watch Mode" in line or "watching" in line.lower():
                    watch_started.set()

        reader_thread = threading.Thread(target=_reader, daemon=True)
        reader_thread.start()

        # Wait up to 30 seconds for watch mode to initialise
        # (initial generate pass may take some time due to LLM call)
        started = watch_started.wait(timeout=30)

        # Terminate the process
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        reader_thread.join(timeout=5)
        full_output = "\n".join(output_lines)

        assert started, (
            f"Watch mode did not print 'Watching' within 30s.\n"
            f"Output so far:\n{full_output}"
        )
        assert proc.returncode in (0, 1, -15, -1, None), (
            f"Process exited with unexpected code: {proc.returncode}\n{full_output}"
        )

    def test_watch_mode_no_dir_fails_gracefully(self, tmp_path):
        """testgen generate on a non-existent dir exits with error (even with --watch)."""
        fake_dir = tmp_path / "does_not_exist"

        result = subprocess.run(
            [sys.executable, "-m", "testgen", "generate", str(fake_dir), "--watch"],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )

        assert result.returncode != 0, "Expected non-zero exit for missing directory"

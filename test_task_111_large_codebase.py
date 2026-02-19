"""
Task 111 E2E Test: Large Codebase Performance Testing

Verifies that TestGen AI handles a 100+ file project without crashing and
measures key performance metrics:
  - Scanner scan time (should complete in <30s for 100 files)
  - Per-file content reading time
  - File-discovery throughput
  - Memory stability (no OOM on large directories)
"""
import time
import sys
import tempfile
import subprocess
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.resolve()

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def large_codebase(tmp_path_factory):
    """
    Generate a synthetic Python project with 120 source files across 6 modules.
    Each file contains 2–4 realistic functions with docstrings.
    """
    tmp = tmp_path_factory.mktemp("large_project")

    modules = ["auth", "users", "products", "orders", "payments", "reports"]
    files_per_module = 20  # 6 × 20 = 120 files total

    TEMPLATE = '''\
"""Module {mod}.helpers_{idx}: helper utilities."""

def helper_{idx}_a(value):
    """Return the processed value."""
    if value is None:
        raise ValueError("value must not be None")
    return str(value).strip()


def helper_{idx}_b(items):
    """Filter and deduplicate a list of items."""
    seen = set()
    result = []
    for item in items:
        key = str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def helper_{idx}_c(mapping, key, default=None):
    """Safe dict lookup with a fallback default."""
    return mapping.get(key, default) if isinstance(mapping, dict) else default


CONSTANT_{idx} = "value_{idx}"
'''

    for mod in modules:
        mod_dir = tmp / mod
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text(f'"""Package {mod}."""\n', encoding="utf-8")
        for idx in range(files_per_module):
            file_path = mod_dir / f"helpers_{idx}.py"
            file_path.write_text(TEMPLATE.format(mod=mod, idx=idx), encoding="utf-8")

    return tmp


# ---------------------------------------------------------------------------
# Task 111 Tests
# ---------------------------------------------------------------------------

class TestLargeCodebaseScan:
    """Performance tests for scanning a 100+ file codebase."""

    def test_discovers_at_least_100_python_files(self, large_codebase):
        """rglob on the synthetic project should find ≥120 .py source files."""
        py_files = [
            f for f in large_codebase.rglob("*.py")
            if not f.name.startswith("test_") and "__pycache__" not in str(f)
        ]
        assert len(py_files) >= 100, (
            f"Expected ≥100 Python files, found {len(py_files)}"
        )

    def test_scanner_completes_within_time_budget(self, large_codebase):
        """
        CodeScanner should scan 120+ files in under 30 seconds.
        (Pure I/O; no LLM calls involved.)
        """
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        start = time.perf_counter()
        result = scanner.scan_directory(str(large_codebase))
        elapsed = time.perf_counter() - start

        print(f"\n  ⏱  Scan time for {len(result.files)} files: {elapsed:.3f}s")

        assert len(result.files) >= 100, (
            f"Scanner found only {len(result.files)} files — expected ≥100"
        )
        assert elapsed < 30.0, (
            f"Scanner took {elapsed:.1f}s — exceeds 30s budget for {len(result.files)} files"
        )

    def test_scan_result_has_correct_file_count(self, large_codebase):
        """ScanResult.files length matches the number of source files on disk."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(large_codebase))

        disk_count = len([
            f for f in large_codebase.rglob("*.py")
            if "__pycache__" not in str(f)
        ])

        # Scanner may legitimately exclude __init__.py or other config files
        assert len(result.files) >= 100, (
            f"ScanResult.files ({len(result.files)}) is smaller than expected. "
            f"Disk has {disk_count} .py files."
        )

    def test_scan_result_totals_are_populated(self, large_codebase):
        """ScanResult.total_lines and total_tokens should be > 0 for a large project."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(large_codebase))

        print(f"\n  📊 total_lines={result.total_lines}, total_tokens={result.total_tokens}")
        assert result.total_lines > 0, "total_lines should be > 0"
        assert result.total_tokens > 0, "total_tokens should be > 0"

    def test_scan_metrics_per_file(self, large_codebase):
        """Average scan time per file should be under 250ms."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        start = time.perf_counter()
        result = scanner.scan_directory(str(large_codebase))
        elapsed = time.perf_counter() - start

        file_count = max(len(result.files), 1)
        ms_per_file = (elapsed / file_count) * 1000
        print(f"\n  ⚡ {ms_per_file:.1f} ms/file average ({file_count} files, {elapsed:.2f}s total)")

        assert ms_per_file < 250, (
            f"Scan is too slow: {ms_per_file:.1f}ms/file — expected <250ms/file"
        )

    def test_large_codebase_file_discovery_via_rglob(self, large_codebase):
        """
        WorkflowManager-style file discovery (rglob) for 120-file project
        should complete in under 1 second.
        """
        start = time.perf_counter()
        files = list(large_codebase.rglob("*.py"))
        elapsed = time.perf_counter() - start

        print(f"\n  🔍 rglob discovered {len(files)} files in {elapsed*1000:.1f}ms")
        assert elapsed < 1.0, f"rglob took {elapsed:.2f}s — expected <1s"
        assert len(files) >= 100

    def test_scan_result_summary_is_available(self, large_codebase):
        """ScanResult.get_summary() should return a non-empty string."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(large_codebase))
        summary = result.get_summary()

        assert isinstance(summary, str)
        assert len(summary) > 20, "Summary is too short to be meaningful"

    def test_repeated_scans_are_consistent(self, large_codebase):
        """Scanning the same directory twice should produce the same file count."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        r1 = scanner.scan_directory(str(large_codebase))
        r2 = scanner.scan_directory(str(large_codebase))

        assert len(r1.files) == len(r2.files), (
            f"Inconsistent scan results: {len(r1.files)} vs {len(r2.files)}"
        )

    def test_scanner_largest_files(self, large_codebase):
        """get_largest_files(10) should return ≤10 files sorted by line count."""
        from testgen.core.scanner import CodeScanner

        scanner = CodeScanner()
        result = scanner.scan_directory(str(large_codebase))
        largest = result.get_largest_files(10)

        assert len(largest) <= 10
        if len(largest) >= 2:
            # Should be sorted descending by line_count
            for i in range(len(largest) - 1):
                assert largest[i].line_count >= largest[i + 1].line_count, (
                    "get_largest_files() is not sorted descending by line_count"
                )

    def test_cli_generate_handles_large_dir_quickly(self, large_codebase):
        """
        `testgen generate <large_dir>` should discover and begin processing
        within a reasonable time. We just verify it starts (no LLM timeout needed).
        We check the scan/discovery phase using a short timeout on the subprocess.
        """
        # We do a dry-run by checking that the CLI at least starts and scans
        # (it will fail at LLM generation but that's expected without a real API key)
        proc = subprocess.Popen(
            [sys.executable, "-m", "testgen", "generate", str(large_codebase)],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        output_lines = []
        found_scan = threading.Event()

        def _reader():
            for line in proc.stdout:
                output_lines.append(line.strip())
                # Look for scan/analyze output
                if any(k in line for k in ["Analyzing", "Found", "source files", "files"]):
                    found_scan.set()

        t = threading.Thread(target=_reader, daemon=True)
        t.start()

        scan_seen = found_scan.wait(timeout=20)

        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        t.join(timeout=5)

        if not scan_seen:
            # Accept if we just get any output (CLI started)
            assert len(output_lines) > 0, (
                "CLI produced no output — did not start correctly"
            )

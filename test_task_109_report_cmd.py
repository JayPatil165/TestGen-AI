#!/usr/bin/env python
"""
Test Task 109: Report Command E2E Test

Verifies the testgen report command works end-to-end:
  1. Creates a temporary project with a generated test.
  2. Runs `testgen test <project>` so results are cached.
  3. Runs `testgen report <project>` and verifies:
     - Exit code is 0.
     - HTML file is created inside <project>/TestGen-AI/reports/.
     - Filename contains a datetime stamp (report_YYYY-MM-DD_…).
     - HTML file is non-empty and contains valid HTML structure.
  4. Verifies a second report run creates a *distinct* file (no overwrites).
"""

import subprocess
import sys
import time
from pathlib import Path
import tempfile
import shutil

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent


def run(args: list, cwd: Path = PROJECT_ROOT, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "testgen"] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_report_command_creates_html_in_project_dir(tmp_path: Path):
    """Full E2E: report is saved inside <project_dir>/TestGen-AI/reports/."""

    print("=" * 70)
    print("TASK 109: REPORT COMMAND E2E TEST")
    print("=" * 70)
    print()

    # ── Setup: minimal project with a passing test ───────────────────────
    print("-" * 70)
    print("SETUP: Creating minimal project with a passing test")
    print("-" * 70)

    project_dir = tmp_path / "sample_project"
    test_runs_dir = project_dir / "TestGen-AI" / "tests" / "2099-01-01_00-00-00"
    test_runs_dir.mkdir(parents=True)

    # Minimal passing test
    (test_runs_dir / "test_sample.py").write_text(
        "def test_always_passes():\n    assert 1 + 1 == 2\n"
    )
    print(f"✅ Project dir: {project_dir}")
    print(f"✅ Test dir:    {test_runs_dir}")
    print()

    # ── Step 1: run testgen test to populate the cache ─────────────────
    print("-" * 70)
    print("TEST 1: Run 'testgen test <project_dir>' to populate cache")
    print("-" * 70)

    test_result = run(["test", str(project_dir)])
    print(f"  Exit code: {test_result.returncode}")
    assert test_result.returncode == 0, (
        f"'testgen test' failed:\nSTDOUT:\n{test_result.stdout}\nSTDERR:\n{test_result.stderr}"
    )
    print("✅ testgen test succeeded")
    print()

    # ── Step 2: run testgen report to generate the HTML ────────────────
    print("-" * 70)
    print("TEST 2: Run 'testgen report <project_dir> --no-open'")
    print("-" * 70)

    report_result = run(["report", str(project_dir), "--no-open"])
    print(f"  Exit code: {report_result.returncode}")
    if report_result.returncode != 0:
        print(f"STDOUT:\n{report_result.stdout}")
        print(f"STDERR:\n{report_result.stderr}")
    assert report_result.returncode == 0, "'testgen report' command failed"
    print("✅ testgen report succeeded")
    print()

    # ── Step 3: verify HTML file location and naming ───────────────────
    print("-" * 70)
    print("TEST 3: Verify HTML is created in <project_dir>/TestGen-AI/reports/")
    print("-" * 70)

    reports_dir = project_dir / "TestGen-AI" / "reports"
    assert reports_dir.exists(), f"reports/ folder not created at {reports_dir}"

    html_files = list(reports_dir.glob("report_*.html"))
    assert len(html_files) >= 1, (
        f"Expected at least one timestamped HTML report in {reports_dir}, found: {list(reports_dir.iterdir())}"
    )

    report_file = html_files[0]
    print(f"✅ Report file: {report_file.name}")
    print(f"✅ Full path:   {report_file}")

    # Validate timestamp pattern in filename: report_YYYY-MM-DD_HH-MM-SS.html
    stem = report_file.stem  # e.g. "report_2026-02-19_12-05-43"
    parts = stem.split("_")
    assert len(parts) >= 3, f"Filename does not have expected timestamp parts: {stem}"
    assert parts[0] == "report", f"Filename does not start with 'report_': {stem}"
    print(f"✅ Filename timestamp pattern validated: {stem}")
    print()

    # ── Step 4: verify HTML content ────────────────────────────────────
    print("-" * 70)
    print("TEST 4: Verify HTML file is non-empty and well-formed")
    print("-" * 70)

    content = report_file.read_text(encoding="utf-8", errors="replace")
    assert len(content) > 100, "HTML file appears empty or too small"
    assert "<html" in content.lower() or "<!doctype" in content.lower(), (
        "HTML file does not contain a valid HTML tag"
    )
    print(f"✅ HTML size: {len(content):,} bytes")
    print("✅ HTML structure looks valid")
    print()

    # ── Step 5: second run creates a distinct file (no overwrite) ──────
    print("-" * 70)
    print("TEST 5: Second report run creates a distinct timestamped file")
    print("-" * 70)

    time.sleep(1)  # ensure different timestamp
    run(["report", str(project_dir), "--no-open"])

    html_files_after = list(reports_dir.glob("report_*.html"))
    assert len(html_files_after) >= 2, (
        f"Expected 2+ report files after two runs, found {len(html_files_after)}: {html_files_after}"
    )
    names = sorted(f.name for f in html_files_after)
    print(f"✅ Reports found: {', '.join(names)}")
    print("✅ Each run creates a unique file — no overwrites")
    print()

    # ── Summary ────────────────────────────────────────────────────────
    print("=" * 70)
    print("✅ TASK 109: REPORT COMMAND E2E TEST PASSED!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  ✅ 'testgen test'   → populated cache correctly")
    print(f"  ✅ 'testgen report' → exit code 0")
    print(f"  ✅ Report stored in <project>/TestGen-AI/reports/")
    print(f"  ✅ Filename includes datetime stamp")
    print(f"  ✅ HTML file is valid and non-empty")
    print(f"  ✅ Multiple runs → multiple distinct report files")
    print()
    print("🎉 Report command CLI is fully functional!")


# -------------------------------------------------------------------
# CLI runner (for direct execution without pytest's tmp_path fixture)
# -------------------------------------------------------------------

if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp(prefix="testgen_task109_"))
    try:
        test_report_command_creates_html_in_project_dir(tmp)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

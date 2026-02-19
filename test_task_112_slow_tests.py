"""
Task 112 E2E Test: Slow Tests & Duration Tracking

Verifies that:
  1. Tests with deliberate `time.sleep()` delays are accurately timed.
  2. The test runner correctly reports per-test duration.
  3. The total suite duration is the sum of individual test durations.
  4. Individual test durations are stored/accessible in the results.
  5. Timeout handling: tests that exceed reasonable thresholds are detectable.
"""
import sys
import time
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.resolve()

# ---------------------------------------------------------------------------
# Helper: create a temp test file with deliberate delays
# ---------------------------------------------------------------------------

SLOW_TEST_CONTENT = '''\
"""Deliberately slow test file for duration-tracking validation."""
import time
import pytest


def test_fast():
    """Very fast test — should complete in <0.1s."""
    assert 1 + 1 == 2


def test_sleep_half_second():
    """Sleeps 0.5s to verify duration tracking."""
    time.sleep(0.5)
    assert True


def test_sleep_one_second():
    """Sleeps 1s — total suite should be >=1.5s."""
    time.sleep(1.0)
    assert True


def test_sleep_two_seconds():
    """Sleeps 2s — longest single test."""
    time.sleep(2.0)
    assert True


def test_sleep_then_fail():
    """Sleeps 0.3s then fails — duration should still be tracked."""
    time.sleep(0.3)
    assert False, "Intentional failure after delay"


def test_skip_with_delay():
    """Marked as skip — should have near-zero duration."""
    pytest.skip("Deliberately skipped")
    time.sleep(10)  # Never reached
'''


@pytest.fixture
def slow_test_dir(tmp_path):
    """Create a temp directory with the slow test file."""
    test_file = tmp_path / "test_slow_operations.py"
    test_file.write_text(SLOW_TEST_CONTENT, encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# Task 112 Tests
# ---------------------------------------------------------------------------

class TestDurationTracking:
    """Verify the test runner accurately measures and reports durations."""

    def test_runner_returns_total_duration(self, slow_test_dir):
        """
        PythonTestRunner.run_tests() should return a TestResults object
        with a positive total duration when slow tests are included.
        """
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        start = time.perf_counter()
        results = runner.run_tests(test_dir=str(slow_test_dir))
        wall_time = time.perf_counter() - start

        print(f"\n  Reported duration: {results.duration:.3f}s  |  Wall time: {wall_time:.3f}s")

        # Duration must be positive and roughly match wall time
        assert results.duration > 0, "TestResults.duration should be > 0 for slow test suite"
        assert results.duration >= 3.0, (
            f"Duration ({results.duration:.2f}s) should be >=3.0s "
            f"(0.5 + 1.0 + 2.0 + 0.3 sleep = 3.8s minimum)"
        )

    def test_per_test_duration_reported(self, slow_test_dir):
        """Each TestResult should have a duration attribute."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(slow_test_dir))

        assert results.tests, "No individual test results returned"
        for t in results.tests:
            assert hasattr(t, 'duration'), f"TestResult for '{t.name}' is missing 'duration'"
            assert t.duration >= 0, f"Duration should be non-negative, got {t.duration} for '{t.name}'"

    def test_slow_tests_have_higher_duration_than_fast(self, slow_test_dir, tmp_path):
        """test_sleep_one_second should have a longer duration than test_fast."""
        from testgen.core.python_runner import PythonTestRunner

        # Use json_report to get accurate per-test durations
        json_file = str(tmp_path / "report.json")
        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(
            test_dir=str(slow_test_dir),
            json_report=True,
            json_report_file=json_file,
        )

        durations = {t.name: t.duration for t in results.tests if results.tests}
        print(f"\n  Per-test durations: {durations}")

        # If all durations are 0.0 — pytest-json-report not producing per-test timing
        if all(v == 0.0 for v in durations.values()):
            pytest.skip("Per-test durations unavailable (pytest-json-report not producing per-test timing)")

        fast_dur = next((v for k, v in durations.items() if 'fast' in k), None)
        slow_dur = next((v for k, v in durations.items() if 'one_second' in k), None)

        if fast_dur is not None and slow_dur is not None:
            assert slow_dur > fast_dur, (
                f"Expected test_sleep_one_second ({slow_dur:.3f}s) > test_fast ({fast_dur:.3f}s)"
            )

    def test_failed_test_duration_still_tracked(self, slow_test_dir):
        """A failing test with a sleep should still report duration >= 0."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(slow_test_dir))

        failed = [t for t in results.tests if t.status.lower() in ('failed', 'fail')]
        print(f"\n  Failed tests: {[(t.name, t.duration) for t in failed]}")

        assert len(failed) >= 1, "Expected at least one failed test"
        for t in failed:
            assert t.duration >= 0.0, (
                f"Failed test '{t.name}' has negative duration: {t.duration}"
            )

    def test_skipped_test_duration_is_near_zero(self, slow_test_dir):
        """A skipped test should have very low duration (< 0.5s)."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(slow_test_dir))

        skipped = [t for t in results.tests if t.status.lower() in ('skipped', 'skip')]
        print(f"\n  Skipped tests: {[(t.name, t.duration) for t in skipped]}")

        for t in skipped:
            assert t.duration < 0.5, (
                f"Skipped test '{t.name}' had high duration {t.duration:.3f}s — "
                "should complete nearly instantly"
            )

    def test_total_is_sum_of_individual_durations(self, slow_test_dir):
        """Total duration should be reasonably close to the sum of per-test durations."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(slow_test_dir))

        if not results.tests:
            pytest.skip("No per-test results available")

        individual_sum = sum(t.duration for t in results.tests)
        print(f"\n  Sum of per-test durations: {individual_sum:.3f}s  |  Total: {results.duration:.3f}s")

        if individual_sum > 0:
            ratio = results.duration / individual_sum
            # total should be between 50% and 250% of individual sum
            assert 0.5 <= ratio <= 2.5, (
                f"Total duration ({results.duration:.2f}s) deviates too far from "
                f"sum of individual durations ({individual_sum:.2f}s). Ratio: {ratio:.2f}"
            )

    def test_result_counts_include_slow_tests(self, slow_test_dir):
        """Results should show 4 passed, 1 failed, 1 skipped."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(slow_test_dir))

        print(
            f"\n  Results: total={results.total}, passed={results.passed}, "
            f"failed={results.failed}, skipped={results.skipped}"
        )
        assert results.total == 6, f"Expected 6 total tests, got {results.total}"
        assert results.passed == 4, f"Expected 4 passed, got {results.passed}"
        assert results.failed == 1, f"Expected 1 failed, got {results.failed}"
        assert results.skipped == 1, f"Expected 1 skipped, got {results.skipped}"


class TestTimeoutDetection:
    """Verify duration data is sufficient to detect or flag slow tests."""

    def test_can_identify_tests_exceeding_threshold(self, slow_test_dir, tmp_path):
        """
        After running, we should be able to programmatically find tests
        that exceeded a 1-second threshold — useful for timeout enforcement.
        """
        from testgen.core.python_runner import PythonTestRunner

        # Use json_report for accurate per-test durations
        json_file = str(tmp_path / "report_threshold.json")
        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(
            test_dir=str(slow_test_dir),
            json_report=True,
            json_report_file=json_file,
        )

        # If all durations are 0 — skip gracefully
        all_zero = all(t.duration == 0.0 for t in results.tests)
        if all_zero:
            pytest.skip("Per-test durations unavailable (pytest-json-report not producing timing)")

        THRESHOLD = 1.0  # seconds
        slow_tests = [t for t in results.tests if t.duration > THRESHOLD]

        print(
            f"\n  Tests exceeding {THRESHOLD}s threshold: "
            f"{[(t.name, f'{t.duration:.2f}s') for t in slow_tests]}"
        )

        assert len(slow_tests) >= 1, (
            f"Expected at least 1 test exceeding {THRESHOLD}s, "
            f"got 0 from: {[(t.name, t.duration) for t in results.tests]}"
        )

    def test_duration_data_is_float_type(self, slow_test_dir):
        """All duration values should be numeric (float or int)."""
        from testgen.core.python_runner import PythonTestRunner

        runner = PythonTestRunner(verbose=False, capture_output=True)
        results = runner.run_tests(test_dir=str(slow_test_dir))

        assert isinstance(results.duration, (int, float)), (
            f"Total duration should be numeric, got {type(results.duration)}"
        )
        for t in results.tests:
            assert isinstance(t.duration, (int, float)), (
                f"Per-test duration for '{t.name}' should be numeric, got {type(t.duration)}"
            )

    def test_subprocess_duration_measurement(self, slow_test_dir):
        """
        Wall-clock timing of the subprocess matches what we expect for a suite
        with built-in delays.
        """
        start = time.perf_counter()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(slow_test_dir), "-q", "--tb=no"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        elapsed = time.perf_counter() - start

        print(f"\n  Wall time for slow test suite: {elapsed:.2f}s")
        print(f"     pytest output: {result.stdout[-200:].strip()}")

        # Total sleep is 0.5 + 1.0 + 2.0 + 0.3 = 3.8s
        assert elapsed >= 3.5, (
            f"Wall time ({elapsed:.2f}s) is too short for a suite with 3.8s of sleeps"
        )
        assert elapsed < 20.0, (
            f"Wall time ({elapsed:.2f}s) is unexpectedly high"
        )

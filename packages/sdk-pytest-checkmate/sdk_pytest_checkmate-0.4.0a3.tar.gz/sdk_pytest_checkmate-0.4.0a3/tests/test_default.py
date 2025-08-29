"""Default test cases demonstrating basic pytest functionality and test states."""

import pytest


def test_passed() -> None:
    """Test that always passes to verify basic functionality."""
    assert True  # noqa: S101


def test_failed() -> None:
    """Test that always fails to demonstrate failure handling."""
    assert False, "This test is designed to fail"  # noqa: B011, PT015, S101


@pytest.mark.skip(reason="Skipping this test for demonstration purposes")
def test_skip() -> None:
    """Test that demonstrates skipping functionality."""


@pytest.mark.xfail(reason="Expected failure for demonstration purposes")
def test_expected_failure() -> None:
    """Test that demonstrates expected failure functionality."""
    assert False, "This test is expected to fail"  # noqa: B011, PT015, S101

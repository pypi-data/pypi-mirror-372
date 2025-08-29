"""Tests demonstrating pytest marker functionality and behavior."""

import pytest


@pytest.mark.title("Title marker DEMO")
def test_marker_title() -> None:
    """Test demonstrating title marker usage."""


@pytest.mark.epic("Epic marker DEMO")
def test_marker_epic() -> None:
    """Test demonstrating epic marker usage."""


@pytest.mark.story("Story marker DEMO")
def test_marker_story() -> None:
    """Test demonstrating story marker usage."""


@pytest.mark.epic("Epic DEMO")
@pytest.mark.story("Story DEMO")
class TestMarkers:
    """Test class for demonstrating multiple markers."""

    @pytest.mark.title("Test with markers DEMO passed")
    def test_markers_passed(self) -> None:
        """Test demonstrating multiple markers with passing assertion."""
        assert True  # noqa: S101

    @pytest.mark.title("Test with markers DEMO failed")
    def test_markers_failed(self) -> None:
        """Test demonstrating multiple markers with failing assertion."""
        assert False  # noqa: B011, PT015, S101

    @pytest.mark.title("Test with markers DEMO skip")
    def test_markers_skip(self) -> None:
        """Test demonstrating multiple markers with skipped assertion."""
        pytest.skip("Skipping this test for demonstration purposes")

    @pytest.mark.title("Test with markers DEMO xfail")
    def test_markers_xfail(self) -> None:
        """Test demonstrating multiple markers with expected failure."""
        pytest.xfail("Expected failure for demonstration purposes")
        assert False  # noqa: B011, PT015, S101

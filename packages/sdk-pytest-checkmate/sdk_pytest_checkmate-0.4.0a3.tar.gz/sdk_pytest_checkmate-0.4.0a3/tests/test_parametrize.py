"""Tests for pytest parametrize functionality with multiple input values."""

import pytest


@pytest.mark.epic("Project functionality")
@pytest.mark.story("Parametrize")
class TestParametrize:
    """Test class for parametrize functionality."""

    @pytest.mark.parametrize(("input_value", "expected"), [(1, 1), (2, 2), (3, 3)])
    @pytest.mark.title("Parametrize test with different inputs without ids")
    def test_parametrize_without_ids(self, input_value: int, expected: int) -> None:
        """Test parametrize with multiple input values."""
        assert input_value == expected, f"Expected {expected}, got {input_value}"  # noqa: S101

    @pytest.mark.parametrize(("input_value", "expected"), [(1, 1), (2, 2), (3, 3)], ids=["one", "two", "three"])
    @pytest.mark.title("Parametrize test with different inputs with ids")
    def test_parametrize_with_ids(self, input_value: int, expected: int) -> None:
        """Test parametrize with multiple input values."""
        assert input_value == expected, f"Expected {expected}, got {input_value}"  # noqa: S101

    @pytest.mark.parametrize(("input_value", "expected"), [(1, 1), (2, 2), (3, 3)])
    def test_parametrize_without_ids_and_title(self, input_value: int, expected: int) -> None:
        """Test parametrize with multiple input values."""
        assert input_value == expected, f"Expected {expected}, got {input_value}"  # noqa: S101

    @pytest.mark.parametrize(("input_value", "expected"), [(1, 1), (2, 2), (3, 3)], ids=["one", "two", "three"])
    def test_parametrize_with_ids_and_title(self, input_value: int, expected: int) -> None:
        """Test parametrize with multiple input values."""
        assert input_value == expected, f"Expected {expected}, got {input_value}"  # noqa: S101

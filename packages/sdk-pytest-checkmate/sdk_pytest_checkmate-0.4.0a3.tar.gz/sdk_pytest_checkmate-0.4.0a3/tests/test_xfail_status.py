"""Tests for xfail status reporting behavior with soft assertions and parametrized tests."""

import pytest

from sdk_pytest_checkmate import soft_assert


@pytest.mark.epic("Project functionality")
@pytest.mark.story("XFAIL Status Reporting")
class TestXfailStatusReporting:
    """Test class for verifying xfail status reporting with soft assertions."""

    @pytest.mark.title("XFAIL with parametrized soft assertions")
    @pytest.mark.xfail(reason="BUG")
    @pytest.mark.parametrize("a", [1, 2, 3])
    def test_one(self, a: int) -> None:
        """Test xfail marker with parametrized soft assertions."""
        soft_assert(a == 1)

    @pytest.mark.title("XFAIL with pytest.xfail() and soft assertions")
    @pytest.mark.xfail(reason="BUG")
    @pytest.mark.parametrize("a", [1, 2, 3])
    def test_two(self, a: int) -> None:
        """Test xfail marker combined with pytest.xfail() call and soft assertions."""
        pytest.xfail("Failing with pytest.xfail()")
        soft_assert(a == 1)

    @pytest.mark.title("Parametrized XFAIL with individual test marking")
    @pytest.mark.parametrize("a", [1, 2, pytest.param(3, marks=pytest.mark.xfail(reason="BUG"))])
    def test_three(self, a: int) -> None:
        """Test parametrized tests with selective xfail marking."""
        soft_assert(a == 3)

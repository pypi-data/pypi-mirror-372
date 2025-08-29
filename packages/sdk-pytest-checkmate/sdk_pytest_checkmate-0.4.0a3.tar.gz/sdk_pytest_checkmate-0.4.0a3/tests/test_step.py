"""Tests for step functionality as function and context manager with soft assertions."""

from time import sleep

import pytest

from sdk_pytest_checkmate import add_data_report, soft_assert, step


@pytest.mark.epic("Project functionality")
@pytest.mark.story("Step Story DEMO")
class TestStep:
    """Test class for step functionality in different usage patterns."""

    @pytest.mark.title("Step function test")
    def test_step_function(self) -> None:
        """Test step used as a function with soft assertions."""
        step("Description for step 1")
        soft_assert(1 == 1, "1 should equal 1")
        step("Description for step 2")
        soft_assert(2 == 2, "2 should equal 2")

    @pytest.mark.title("Step context manager test")
    def test_step_context(self) -> None:
        """Test step used as context manager with timing and soft assertions."""
        with step("Description for step 1"):
            sleep(0.2)
            soft_assert(1 == 1, "1 should equal 1")
        with step("Description for step 2"):
            soft_assert(2 == 2, "2 should equal 2")

    @pytest.mark.title("Step with soft_assert")
    def test_step_with_soft_assert(self) -> None:
        """Test multiple steps as context managers with various soft assertions."""
        with step("Description for step 1"):
            soft_assert(1 == 1, "1 should equal 1")
        with step("Description for step 2"):
            sleep(0.2)
            soft_assert(2 == 2, "2 should equal 2")
            soft_assert(3 == 3, "3 should equal 3")
        with step("Description for step 3"):
            sleep(0.2)
            soft_assert(4 == 4, "4 should equal 4")
            soft_assert(5 == 5, "5 should equal 5")

    @pytest.mark.title("Step with soft_assert and add_data_report")
    def test_step_with_soft_assert_and_add_data_report(self) -> None:
        """Test multiple steps as context managers with various soft assertions and data reporting."""
        with step("Description for step 1"):
            soft_assert(1 == 1, "1 should equal 1")
            add_data_report(1, "Step 1 data")
        with step("Description for step 2"):
            sleep(0.2)
            soft_assert(2 == 2, "2 should equal 2")
            soft_assert(3 == 3, "3 should equal 3")
            add_data_report([2, 3], "Step 2 data")
        with step("Description for step 3"):
            sleep(0.2)
            soft_assert(4 == 4, "4 should equal 4")
            soft_assert(5 == 5, "5 should equal 5")
            add_data_report({"step": 3, "value": 5}, "Step 3 data")

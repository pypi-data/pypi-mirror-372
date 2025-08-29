"""Tests for soft assertion functionality and behavior with various scenarios."""

import pytest

from sdk_pytest_checkmate import soft_assert


@pytest.mark.epic("Project functionality")
@pytest.mark.story("Soft Assert Story DEMO")
class TestSoftAssert:
    """Test class for soft assertion functionality with markers."""

    @pytest.mark.title("Soft assert passed test with Markers")
    def test_soft_assert_markers_passed(self) -> None:
        """Test soft assertions that all pass successfully."""
        soft_assert(1 == 1, "1 should equal 1")
        soft_assert(2 == 2, "2 should equal 2")

    @pytest.mark.title("Soft assert failed test with Markers")
    def test_soft_assert_markers_failed(self) -> None:
        """Test soft assertions that all fail."""
        soft_assert(1 == 2, "1 should equal 2")
        soft_assert(2 == 3, "2 should equal 3")

    @pytest.mark.title("Soft assert mixed test with Markers")
    def test_soft_assert_markers_mixed(self) -> None:
        """Test soft assertions with mixed pass and fail results."""
        soft_assert(1 == 1, "1 should equal 1")
        soft_assert(2 == 3, "2 should equal 3")
        soft_assert(2 == 2, "2 should equal 2")
        soft_assert(3 == 4, "3 should equal 4")

    @pytest.mark.title("Soft assert skip test without Markers")
    def test_soft_assert_skip(self) -> None:
        """Test demonstrating skipped soft assertion test."""
        pytest.skip("Skipping this test for demonstration purposes")
        soft_assert(1 == 1, "1 should equal 1")

    @pytest.mark.title("Soft assert xfail test without Markers")
    def test_soft_assert_xfail(self) -> None:
        """Test demonstrating expected failure in soft assertion."""
        pytest.xfail("Expected failure for demonstration purposes")
        soft_assert(1 == 2, "1 should equal 2")

    @pytest.mark.title("Soft assert with custom details")
    def test_soft_assert_with_custom_details(self) -> None:
        """Test soft_assert with custom details to ensure they override auto-generation."""
        age = 25
        soft_assert(age > 30, "Age validation failed", details="Custom: User must be over 30")
        soft_assert(
            age < 20,
            "Age validation failed",
            details=["Custom validation", "Age boundary check", "Must be under 20"],
        )

    @pytest.mark.title("Soft assert basic test")
    def test_soft_assert_basic(self) -> None:
        """Test various complex soft_assert scenarios."""
        name = "name"
        soft_assert(name == "nae", "String mismatch")

        # Dictionary method calls
        soft_assert({"id": 123}.get("id") == 123, "ID should be 123")
        soft_assert({"id": 123}.get("id") == 456, "ID should be 456 (will fail)")

        # List operations
        list_name = ["test1", "test2"]
        soft_assert(len(list_name) == 2, "List should contain 2 items")
        soft_assert(len(list_name) == 3, "List should contain 3 items (will fail)")

        # More complex expressions
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        soft_assert(len(data["users"]) > 1, "Should have multiple users")
        soft_assert(data["users"][0]["name"] == "Alice", "First user should be Alice")
        soft_assert(data["users"][0]["name"] == "Charlie", "First user should be Charlie (will fail)")

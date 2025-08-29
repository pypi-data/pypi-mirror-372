"""Tests for adding various Python data types to the test report using the add_data_report function."""

import pytest

from sdk_pytest_checkmate import add_data_report


@pytest.mark.epic("Project functionality")
@pytest.mark.story("Data in Report Story DEMO")
class TestDataInReport:
    """Tests for adding various data types to the test report."""

    @pytest.mark.title("Add data to report test")
    def test_add_string_to_report(self) -> None:
        """Check adding string data to report."""
        add_data_report("Simple text", "String data")

    @pytest.mark.title("Add integer data to report test")
    def test_add_integer_to_report(self) -> None:
        """Check adding integer data to report."""
        add_data_report(12345, "Integer data")

    @pytest.mark.title("Add float data to report test")
    def test_add_float_to_report(self) -> None:
        """Check adding float data to report."""
        add_data_report(3.14159, "Float data")

    @pytest.mark.title("Add list data to report test")
    def test_add_list_to_report(self) -> None:
        """Check adding list data to report."""
        add_data_report([1, 2, 3, 4, 5], "List data")

    @pytest.mark.title("Add None data to report test")
    def test_add_none_to_report(self) -> None:
        """Check adding None data to report."""
        add_data_report(None, "None data")

    @pytest.mark.title("Add boolean data to report test")
    def test_add_boolean_to_report(self) -> None:
        """Check adding boolean data to report."""
        add_data_report(True, "Boolean data")

    @pytest.mark.title("Add dictionary data to report test")
    def test_add_dictionary_to_report(self) -> None:
        """Check adding dictionary data to report."""
        add_data_report({"key": "value", "number": 42}, "Dictionary data")

    @pytest.mark.title("Add nested dictionary data to report test")
    def test_add_nested_dictionary_to_report(self) -> None:
        """Check adding nested dictionary data to report."""
        add_data_report({"nested": {"a": 1, "b": [1, 2, 3]}}, "Nested Dictionary data")

    @pytest.mark.title("Add tuple data to report test")
    def test_add_tuple_to_report(self) -> None:
        """Check adding tuple data to report."""
        add_data_report((10, 20, 30), "Tuple data")  # type: ignore

    @pytest.mark.title("Add set data to report test")
    def test_add_set_to_report(self) -> None:
        """Check adding set data to report."""
        add_data_report({1, 2, 3}, "Set data")  # type: ignore

    @pytest.mark.title("Add bytes data to report test")
    def test_add_bytes_to_report(self) -> None:
        """Check adding bytes data to report."""
        add_data_report(b"byte data", "Bytes data")  # type: ignore

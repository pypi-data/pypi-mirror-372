"""Tests for JSON validation functionality with various schema validation scenarios."""

import pytest

from sdk_pytest_checkmate import soft_validate_json


@pytest.mark.epic("Project functionality")
@pytest.mark.story("JSON Validation")
class TestJsonValidation:
    """Test class for JSON schema validation with valid, invalid, and complex structures."""

    @pytest.mark.title("Valid JSON Test")
    def test_valid_json(self) -> None:
        """Test valid JSON structure."""
        json_data = {"key": "value"}
        soft_validate_json(json_data, schema={"type": "object", "properties": {"key": {"type": "string"}}})

    @pytest.mark.title("Invalid JSON Test")
    def test_invalid_json(self) -> None:
        """Test invalid JSON structure."""
        json_data = {"key": 123}
        soft_validate_json(json_data, schema={"type": "object", "properties": {"key": {"type": "string"}}})

    @pytest.mark.title("Complex JSON Test")
    def test_complex_json(self) -> None:
        """Test complex JSON structure."""
        json_data = {
            "key": "value",
            "nested": {
                "key": "value",
            },
        }
        schema = {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "nested": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                    },
                },
            },
        }
        soft_validate_json(json_data, schema=schema)

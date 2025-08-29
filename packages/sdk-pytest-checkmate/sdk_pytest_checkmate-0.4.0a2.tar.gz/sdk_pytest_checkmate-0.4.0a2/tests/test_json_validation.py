"""Tests for JSON validation functionality with various schema validation scenarios."""

import pytest

from sdk_pytest_checkmate import soft_validate_json, soft_assert


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

    @pytest.mark.title("Invalid JSON Schema Test")
    def test_invalid_json_schema(self) -> None:
        """Test validation with invalid JSON schema definition."""
        json_data = {"key": 123}
        soft_validate_json(json_data, schema={"type": "object", "properties": {"key": {"type": None}}})

    @pytest.mark.title("Empty Schema Test")
    def test_empty_schema_allows_any_data(self) -> None:
        """Test that empty schema {} allows any data (this is correct JSON Schema behavior)."""
        json_data = {"key": 123}
        soft_validate_json(json_data, schema={})

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

    @pytest.mark.title("Strict Validation - Valid Data")
    def test_strict_validation_valid_data(self) -> None:
        """Test strict validation with valid data - should pass."""
        json_data = {"key": "value"}
        schema = {"type": "object", "properties": {"key": {"type": "string"}}}
        soft_validate_json(json_data, schema=schema, strict=True)
        soft_assert(True, "Strict validation passed")

    @pytest.mark.title("Strict Validation - Invalid Data")
    def test_strict_validation_invalid_data(self) -> None:
        """Test strict validation with invalid data - should fail immediately."""
        json_data = {"key": 123}
        schema = {"type": "object", "properties": {"key": {"type": "string"}}}
        soft_validate_json(json_data, schema=schema, strict=True)
        soft_assert(True, "Strict validation passed")

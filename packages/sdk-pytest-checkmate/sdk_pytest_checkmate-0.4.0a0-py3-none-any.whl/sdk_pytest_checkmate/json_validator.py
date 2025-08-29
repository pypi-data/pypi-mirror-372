"""JSON Schema validation utilities for pytest-checkmate.

This module provides functions for validating JSON data against JSON Schema
specifications using soft assertions that integrate with the pytest-checkmate
reporting system.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from jsonschema import validators
from referencing.jsonschema import EMPTY_REGISTRY

from sdk_pytest_checkmate import soft_assert


def _load_json_schema(path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON schema from a file path.

    Args:
        path: File path to the JSON schema file. Can be a string or Path object.

    Returns:
        Dict containing the loaded JSON schema.

    """
    path_obj = Path(path)
    with path_obj.open("r", encoding="utf-8") as file:
        schema = json.load(file)
    return schema


def _validate(data: Any, schema: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate data against a JSON schema.

    Args:
        data: The data to validate (can be any JSON-serializable type).
        schema: The JSON schema to validate against.

    Returns:
        A tuple containing:
        - bool: True if validation passes, False if it fails.
        - str: Success message or formatted error message with validation details.
    """
    validator_class = validators.validator_for(schema)
    validator = validator_class(schema, registry=EMPTY_REGISTRY)
    errors = [
        f"\t- ({'/'.join(str(p) for p in error.path)}) {error.message}"
        for error in validator.iter_errors(data)
    ]
    if errors:
        return (False, "Validation JSONSchema:\n" + "\n".join(errors))
    return (True, "Validation JSONSchema")


def soft_validate_json(
    data: Any,
    *,
    schema: Optional[Dict[str, Any]] = None,
    schema_path: Optional[Union[str, Path]] = None,
) -> None:
    """Validate JSON data against a schema using soft assertion.

    This function performs JSON schema validation and reports failures through
    the soft assertion mechanism, allowing tests to continue even when validation
    fails while still capturing the failure for reporting.

    Args:
        data: The data to validate. Can be any JSON-serializable Python object
              (dict, list, str, int, float, bool, None).
        schema: The JSON schema as a dictionary. If provided, this takes precedence
                over schema_path.
        schema_path: Path to a JSON schema file. Used only if schema is None.
                     Can be a string or Path object.

    Returns:
        None. Validation results are reported through the soft assertion system.

    Raises:
        ValueError: If neither schema nor schema_path is provided.
        FileNotFoundError: If schema_path is provided but the file doesn't exist.
        json.JSONDecodeError: If schema_path points to a file with invalid JSON.

    Example:
        >>> # Validate with inline schema
        >>> schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        >>> data = {"name": "test"}
        >>> soft_validate_json(data, schema=schema)

        >>> # Validate with schema file
        >>> soft_validate_json(data, schema_path="path/to/schema.json")
    """
    if schema is None and schema_path is not None:
        schema = _load_json_schema(schema_path)
    if schema is None:
        raise ValueError(
            "JSON Schema must be provided either directly or via schema_path."
        )
    check, error = _validate(data, schema)
    soft_assert(check, error)

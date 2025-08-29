"""Tests for environment variable handling."""

from os import getenv

import pytest

from sdk_pytest_checkmate import add_data_report


@pytest.mark.epic("Project functionality")
@pytest.mark.story("ENV variables")
@pytest.mark.title("Test environment variables")
def test_env_variables() -> None:
    """Test reading environment variables and adding them to data reports."""
    api_base_url = getenv("API_BASE_URL")
    api_key = getenv("API_KEY")
    add_data_report(api_base_url, "The value for `API_BASE_URL` from .env.example ")
    add_data_report(api_key, "The value for `API_KEY` from .env.example ")

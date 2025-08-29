"""Configuration management for pytest options and environment loading."""

import os
from pathlib import Path

import pytest

from ._constants import DEFAULT_ENV_FILENAME, DEFAULT_REPORT_FILENAME, DEFAULT_REPORT_TITLE
from ._types import AnyType


class EnvironmentLoader:
    """Handles loading environment variables from .env files."""

    @staticmethod
    def _parse_env_line(line: str) -> tuple[str, str] | None:
        """Parse a single line from an .env file.

        Args:
            line: The line to parse.

        Returns:
            A tuple of (key, value) if the line contains a valid assignment,
            None otherwise.
        """
        line = line.strip()

        if not line or line.startswith("#"):
            return None

        if "=" not in line:
            return None

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        return (key, value) if key else None

    @classmethod
    def load_env_file(cls, file_path: str) -> bool:
        """Load environment variables from a .env file.

        Args:
            file_path: Path to the .env file.

        Returns:
            True if the file was successfully loaded, False otherwise.
        """
        try:
            env_path = Path(file_path)
            if not env_path.exists():
                return False

            with env_path.open(encoding="utf-8") as f:
                for _line_num, line in enumerate(f, 1):
                    parsed = cls._parse_env_line(line)
                    if parsed is None:
                        continue

                    key, value = parsed
                    if key not in os.environ:
                        os.environ[key] = value

            return True
        except Exception:
            return False


class PytestConfigManager:
    """Manages pytest configuration options and markers."""

    @staticmethod
    def add_pytest_options(parser: AnyType) -> None:
        """Add checkmate-specific command line options to pytest.

        Args:
            parser: The pytest argument parser.
        """
        group = parser.getgroup("checkmate")

        group.addoption(
            "--report-html",
            action="store",
            nargs="?",
            const=DEFAULT_REPORT_FILENAME,
            dest="report_html",
            help=f"Generate HTML report (optional path, default: {DEFAULT_REPORT_FILENAME})",
        )

        group.addoption(
            "--report-title",
            action="store",
            dest="report_title",
            default=DEFAULT_REPORT_TITLE,
            help="Title for the HTML report header and <title>.",
        )

        group.addoption(
            "--report-json",
            action="store",
            dest="report_json",
            default=None,
            help="Path to write JSON results (optional).",
        )

        group.addoption(
            "--env-file",
            action="store",
            dest="env_file",
            default=DEFAULT_ENV_FILENAME,
            help=f"Path to .env file to load environment variables (default: {DEFAULT_ENV_FILENAME})",
        )

    @staticmethod
    def configure_pytest_markers(config: pytest.Config) -> None:
        """Configure custom pytest markers.

        Args:
            config: The pytest configuration object.
        """
        markers = [
            ("title(name)", "Custom test title for human-readable display in reports"),
            ("epic(name)", "Group tests under an epic for better organization"),
            ("story(name)", "Group tests under a story within an epic for detailed organization"),
        ]

        for marker_definition, description in markers:
            config.addinivalue_line("markers", f"{marker_definition}: {description}")


def load_env_file(file_path: str) -> bool:
    """Load environment variables from a .env file.

    Args:
        file_path: Path to the .env file.

    Returns:
        True if successful, False otherwise.

    Note:
        This is a legacy function. Use EnvironmentLoader.load_env_file() instead.
    """
    return EnvironmentLoader.load_env_file(file_path)


def add_pytest_options(parser: AnyType) -> None:
    """Add pytest command line options.

    Args:
        parser: The pytest argument parser.

    Note:
        This is a legacy function. Use PytestConfigManager.add_pytest_options() instead.
    """
    PytestConfigManager.add_pytest_options(parser)


def configure_pytest_markers(config: pytest.Config) -> None:
    """Configure pytest markers.

    Args:
        config: The pytest configuration object.

    Note:
        This is a legacy function. Use PytestConfigManager.configure_pytest_markers() instead.
    """
    PytestConfigManager.configure_pytest_markers(config)

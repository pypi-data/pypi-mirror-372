"""Constants used throughout the SDK."""

from typing import Final

# Test status constants
TEST_STATUS_PASSED: Final[str] = "PASSED"
TEST_STATUS_FAILED: Final[str] = "FAILED"
TEST_STATUS_ERROR: Final[str] = "ERROR"
TEST_STATUS_SKIPPED: Final[str] = "SKIPPED"
TEST_STATUS_XFAIL: Final[str] = "XFAIL"
TEST_STATUS_XPASS: Final[str] = "XPASS"

# Report defaults
DEFAULT_REPORT_FILENAME: Final[str] = "report.html"
DEFAULT_REPORT_TITLE: Final[str] = "Pytest report"
DEFAULT_ENV_FILENAME: Final[str] = ".env"
DEFAULT_TIMEOUT: Final[float] = 10.0

# HTML report constants
MAX_OUTPUT_SIZE: Final[int] = 60 * 1024  # 60KB
MAX_DETAIL_HEIGHT: Final[str] = "340px"
DEFAULT_LINE_HEIGHT: Final[str] = "1.4"

# Error messages
ERROR_NO_CONTEXT: Final[str] = "get_context() called outside of test context"
ERROR_NO_SCHEMA: Final[str] = "JSON Schema must be provided either directly or via schema_path."

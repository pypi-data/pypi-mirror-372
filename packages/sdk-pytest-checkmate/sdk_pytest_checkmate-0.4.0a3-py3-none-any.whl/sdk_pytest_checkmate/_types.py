"""Type definitions and protocols for the SDK."""

from typing import Any, Protocol, TypedDict

# Type aliases
AnyType = Any
TestData = dict[str, Any]
TestResults = list[TestData]
JsonData = dict[str, Any] | list[Any] | str | int | float | bool | None


__all__ = [
    "AnyType",
    "HttpRequest",
    "HttpResponse",
    "JsonData",
    "ResponseTime",
    "TestContext",
    "TestData",
    "TestReport",
    "TestResults",
]


class TestContext(TypedDict):
    """Type definition for test context dictionary."""

    steps: list[Any]
    soft_failures: list[str]
    soft_checks: list[Any]
    data_reports: list[Any]
    seq: int


class TestReport(TypedDict):
    """Type definition for test report data."""

    name: str
    title: str
    status: str
    duration: float
    short: str
    full: str
    steps: list[dict[str, Any]]
    soft_checks: list[dict[str, Any]]
    data_reports: list[dict[str, Any]]
    epic: str | None
    story: str | None
    params: dict[str, str]


class HttpRequest(Protocol):
    """Protocol for HTTP request objects."""

    @property
    def method(self) -> str:
        """HTTP method."""
        ...

    @property
    def content(self) -> bytes:
        """Request content as bytes."""
        ...

    @property
    def headers(self) -> dict[str, str]:
        """Request headers."""
        ...


class ResponseTime(Protocol):
    """Protocol for response time objects."""

    def total_seconds(self) -> float:
        """Get total seconds as float."""
        ...


class HttpResponse(Protocol):
    """Protocol for HTTP response objects."""

    @property
    def status_code(self) -> int:
        """HTTP status code."""
        ...

    @property
    def headers(self) -> dict[str, str]:
        """Response headers."""
        ...

    @property
    def content(self) -> bytes:
        """Response content as bytes."""
        ...

    @property
    def url(self) -> str:
        """Response URL."""
        ...

    @property
    def request(self) -> HttpRequest:
        """Request object."""
        ...

    @property
    def elapsed(self) -> ResponseTime:
        """Response time information."""
        ...

    def json(self) -> JsonData:
        """Parse response content as JSON."""
        ...

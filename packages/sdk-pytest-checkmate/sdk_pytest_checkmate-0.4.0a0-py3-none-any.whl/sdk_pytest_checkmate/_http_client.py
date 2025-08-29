"""Enhanced HTTP client with automatic request/response logging."""

import json

from httpx import URL, AsyncClient, Client, Response

from ._core import add_data_report
from ._types import AnyType, JsonData


def _try_parse_json(data: bytes | str | None) -> JsonData:
    """Attempt to parse data as JSON, returning original data if parsing fails.

    Args:
        data: The data to parse as JSON.

    Returns:
        Parsed JSON data or original data if parsing fails.
    """
    if data is None or data == b"" or data == "":
        return None

    try:
        data_str = data.decode("utf-8") if isinstance(data, bytes) else str(data)
        return json.loads(data_str)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return str(data)


def _format_response_time(elapsed_seconds: float) -> str:
    """Format response time for display.

    Args:
        elapsed_seconds: Response time in seconds.

    Returns:
        Formatted response time string.
    """
    milliseconds = elapsed_seconds * 1000
    return f"{milliseconds:.3f} ms"


def _create_request_log(response: Response) -> dict[str, AnyType]:
    """Create a structured log entry for an HTTP request/response pair.

    Args:
        response: The HTTP response object.

    Returns:
        A dictionary containing request and response information.
    """
    return {
        "method": response.request.method,
        "url": str(response.url),
        "request_headers": dict(response.request.headers),
        "request_body": _try_parse_json(response.request.content),
        "status_code": response.status_code,
        "response_time": _format_response_time(response.elapsed.total_seconds()),
        "response_headers": dict(response.headers),
        "response_body": _try_parse_json(response.content),
    }


class HttpClient(Client):
    """Enhanced HTTP client that automatically logs requests and responses.

    This client extends httpx.Client to provide automatic logging of all
    HTTP requests and responses to the test report timeline.
    """

    def request(self, method: str, url: URL | str, **kwargs: AnyType) -> Response:
        """Execute an HTTP request and log the details.

        Args:
            method: HTTP method (GET, POST, etc.).
            url: Request URL.
            **kwargs: Keyword arguments passed to the parent request method.

        Returns:
            The HTTP response object.
        """
        response = super().request(method, url, **kwargs)

        log_entry = _create_request_log(response)

        label = f"HTTP request to `{response.request.method} {response.url}` [{response.status_code}]"
        add_data_report(log_entry, label)

        return response


class AsyncHttpClient(AsyncClient):
    """Enhanced async HTTP client that automatically logs requests and responses.

    This client extends httpx.AsyncClient to provide automatic logging of all
    HTTP requests and responses to the test report timeline.
    """

    async def request(self, method: str, url: URL | str, **kwargs: AnyType) -> Response:
        """Execute an async HTTP request and log the details.

        Args:
            method: HTTP method (GET, POST, etc.).
            url: Request URL.
            **kwargs: Keyword arguments passed to the parent request method.

        Returns:
            The HTTP response object.
        """
        response = await super().request(method, url, **kwargs)

        log_entry = _create_request_log(response)

        label = f"HTTP request to `{response.request.method} {response.url}` [{response.status_code}]"
        add_data_report(log_entry, label)

        return response

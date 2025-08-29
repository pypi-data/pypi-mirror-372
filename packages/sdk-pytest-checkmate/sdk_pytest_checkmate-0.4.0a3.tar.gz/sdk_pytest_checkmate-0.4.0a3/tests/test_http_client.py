"""Tests for HTTP client functionality with various request types and fixtures."""

from collections.abc import Generator

import pytest

from sdk_pytest_checkmate import soft_assert, step
from sdk_pytest_checkmate._http_client import HttpClient


@pytest.fixture(scope="session")
def http_client() -> Generator[HttpClient, None, None]:
    """Fixture providing a session-scoped HTTP client for httpbin.org."""
    client = HttpClient(base_url="https://httpbin.org")
    yield client
    client.close()


@pytest.mark.epic("Project functionality")
@pytest.mark.story("HTTP Client")
class TestHttpClient:
    """Test class for HTTP client functionality."""

    @pytest.mark.title("HTTP Client Test")
    def test_http_client_simple(self) -> None:
        """Test simple HTTP client POST request without steps."""
        client = HttpClient(base_url="https://httpbin.org")
        response = client.post("/post", json={"key": "value"})
        soft_assert(response.status_code == 200, "POST request should succeed")

    @pytest.mark.title("HTTP Client Test with step")
    def test_http_client_sequential_requests(self) -> None:
        """Test HTTP client with sequential GET and POST requests using step context managers."""
        client = HttpClient(base_url="https://httpbin.org")
        with step("GET /get request"):
            response = client.get("/get", params={"param1": "value1"})
            soft_assert(response.status_code == 200, "GET request should succeed")
        with step("POST /post request"):
            response = client.post("/post", json={"key": "value"})
            soft_assert(response.status_code == 200, "POST request should succeed")

    @pytest.mark.title("HTTP Client Test with Fixture")
    def test_http_client_fixture(self, http_client: HttpClient) -> None:
        """Test HTTP client using session-scoped fixture with step context manager."""
        with step("GET /get request"):
            response = http_client.get("/get", params={"param1": "value1"})
            soft_assert(response.status_code == 200, "GET request should succeed")

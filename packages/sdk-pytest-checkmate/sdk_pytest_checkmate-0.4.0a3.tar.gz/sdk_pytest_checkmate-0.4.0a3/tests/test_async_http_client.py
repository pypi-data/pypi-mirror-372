"""Tests for async HTTP client functionality with various request types and fixtures."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

from sdk_pytest_checkmate import soft_assert, step
from sdk_pytest_checkmate._http_client import AsyncHttpClient


@pytest_asyncio.fixture
async def async_http_client() -> AsyncGenerator[AsyncHttpClient, None]:
    """Fixture providing an async HTTP client for httpbin.org."""
    client = AsyncHttpClient(base_url="https://httpbin.org")
    yield client
    await client.aclose()


@pytest.mark.epic("Project functionality")
@pytest.mark.story("Async HTTP Client")
class TestAsyncHttpClient:
    """Test class for async HTTP client functionality."""

    @pytest.mark.title("Async HTTP Client Test")
    @pytest.mark.asyncio
    async def test_async_http_client_simple(self) -> None:
        """Test simple async HTTP client POST request without steps."""
        client = AsyncHttpClient(base_url="https://httpbin.org")
        response = await client.post("/post", json={"key": "value"})
        soft_assert(response.status_code == 200, "POST request should succeed")
        await client.aclose()

    @pytest.mark.title("Async HTTP Client Test with step")
    @pytest.mark.asyncio
    async def test_async_http_client_sequential_requests(self) -> None:
        """Test async HTTP client with sequential GET and POST requests using step context managers."""
        client = AsyncHttpClient(base_url="https://httpbin.org")
        with step("GET /get request"):
            response = await client.get("/get", params={"param1": "value1"})
            soft_assert(response.status_code == 200, "GET request should succeed")
        with step("POST /post request"):
            response = await client.post("/post", json={"key": "value"})
            soft_assert(response.status_code == 200, "POST request should succeed")
        await client.aclose()

    @pytest.mark.title("Async HTTP Client Test with Fixture")
    @pytest.mark.asyncio
    async def test_async_http_client_fixture(self, async_http_client: AsyncHttpClient) -> None:
        """Test async HTTP client using session-scoped fixture with step context manager."""
        with step("GET /get request"):
            response = await async_http_client.get("/get", params={"param1": "value1"})
            soft_assert(response.status_code == 200, "GET request should succeed")

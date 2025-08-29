# Key Features

## SDK API Functions

- `step(name: str)` - Context manager for creating steps
- `soft_assert(condition, message, details)` - Soft assertion
- `add_data_report(data, label)` - Add data to report
- `HttpClient(base_url, **kwargs)` - HTTP client
- `AsyncHttpClient(base_url, **kwargs)` - Asynchronous HTTP client
- `soft_validate_json(data, schema, schema_path, strict)` - JSON data validation

## Test Steps

### step(name: str)

Context manager for recording test steps with execution time information.

**Parameters:**
- `name`: Clear step name that appears in the HTML report

```python
from sdk_pytest_checkmate import step

def test_example():
    with step("Data preparation"):
        data = {"name": "Test"}
    
    with step("Operation execution"):
        result = process_data(data)
    
    with step("Result verification"):
        assert result is not None

# Async usage
@pytest.mark.asyncio
async def test_async_example():
    async with step("Async operation"):
        result = await async_operation()
```

## Soft Assertions

### soft_assert(condition: bool, message: str = None, details: str | list[str] = None) -> bool

Records a non-critical assertion that does not stop the test immediately upon failure.

**Parameters:**
- `condition`: Boolean expression to evaluate
- `message`: Optional descriptive message (default "Soft assertion")
- `details`: Optional argument providing additional details for the report (by default shows the expression for evaluation)

**Returns:** Boolean value `condition`

```python
from sdk_pytest_checkmate import soft_assert

def test_validation():
    data = {"name": "John", "age": 25}
    
    soft_assert(data["name"] == "John", "Name should be John")
    soft_assert(data["age"] > 18, "Age should be greater than 18")
    soft_assert("email" in data, "Email should be present")
    
    # Test will continue even if some assertions fail
    # and will be marked as FAILED only at the end

# With custom details
def test_with_details():
    age = 25
    soft_assert(age > 30, "Age check", 
                details="User should be older than 30 years")
    soft_assert(age < 20, "Range check", 
                details=["Custom validation", "Age range verification"])
```

## HTTP Clients

### HttpClient(base_url: str, **kwargs)

HTTP client with automatic display of requests/responses in HTML report.

**Parameters:**
- `base_url`: Base URL for all HTTP requests
- `**kwargs`: Additional arguments passed to httpx.Client

```python
from sdk_pytest_checkmate import HttpClient

def test_api():
    # Basic usage
    client = HttpClient("https://api.example.com")
    
    # With additional parameters
    client = HttpClient(
        "https://api.example.com",
        headers={"Authorization": "Bearer token"},
        timeout=30.0,
        verify=False
    )
    
    # All requests are automatically logged to the report
    response = client.get("/users")
    assert response.status_code == 200
```

### AsyncHttpClient(base_url: str, **kwargs)

Asynchronous HTTP client with automatic display of requests/responses in HTML report.

**Parameters:**
- `base_url`: Base URL for all HTTP requests
- `**kwargs`: Additional arguments passed to httpx.AsyncClient

```python
from sdk_pytest_checkmate import AsyncHttpClient
import pytest

@pytest.mark.asyncio
async def test_async_api():
    async with AsyncHttpClient("https://api.example.com") as client:
        response = await client.get("/users")
        assert response.status_code == 200

# Or without context manager
@pytest.mark.asyncio
async def test_async_api_simple():
    client = AsyncHttpClient("https://api.example.com")
    response = await client.get("/users")
    assert response.status_code == 200
    await client.aclose()  # Don't forget to close the client
```

## JSON Validation

### soft_validate_json(data: JsonData, *, schema: dict[str, Any] | None = None, schema_path: str | Path | None = None, strict: bool = False) -> None:

Validates JSON data against JSON Schema specification.

\*type JsonData = dict[str, Any] | list[Any] | str | int | float | bool | None

**Parameters:**
- `data`: Any JSON-serializable Python object (dict, list, str, int, float, bool, None)
- `schema`: JSON Schema as dictionary (optional, mutually exclusive with schema_path)
- `schema_path`: Path to JSON Schema file (optional, used if schema is not provided)
- `strict`: If True, raises JsonValidationError on validation failure instead of soft assertion.

```python
from sdk_pytest_checkmate import soft_validate_json

def test_json_validation():
    # Validation with inline schema
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "age"]
    }
    
    data = {
        "name": "John",
        "age": 25,
        "email": "john@example.com",
    }
    soft_validate_json(data, schema=schema)

# Validation from schema file
def test_json_from_file():
    user_data = {"id": 1, "username": "john", "email": "john@test.com"}
    soft_validate_json(user_data, schema_path="schemas/user.json")
```

## Data Attachment

### add_data_report(data: Any, label: str) -> DataRecord

Attaches arbitrary data to the test timeline for review in HTML reports.

**Parameters:**
- `data`: Any Python object (dict/list will be beautifully formatted as JSON)
- `label`: Short label shown in the report interface

```python
from sdk_pytest_checkmate import add_data_report

def test_with_data():
    # Attach configuration
    config = {"endpoint": "/api/users", "timeout": 30}
    add_data_report(config, "API Configuration")
```

## pytest Markers

The SDK supports special markers for organizing tests:

```python
import pytest

@pytest.mark.epic("User Management")        # Group by epics
@pytest.mark.story("User Registration")     # Group by stories
@pytest.mark.title("New user registration")  # Custom test title
def test_user_registration():
    with step("Data preparation"):
        user_data = {"name": "John", "email": "john@test.com"}
        add_data_report(user_data, "User Data")
```

## Environment Variables

The SDK automatically supports loading variables from `.env` files:

```bash
# Run with custom .env file
pytest --env-file=test.env --report-html=report.html

# Uses .env by default
pytest --report-html=report.html
```

```python
# .env file
API_BASE_URL=https://staging.api.com
API_TOKEN=test_token_123
TIMEOUT=30

# In tests
import os
from sdk_pytest_checkmate import HttpClient

def test_with_env_vars():
    base_url = os.getenv('API_BASE_URL', 'http://localhost')
    token = os.getenv('API_TOKEN')
    timeout = int(os.getenv('TIMEOUT', '10'))
    
    client = HttpClient(
        base_url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout
    )
    
    response = client.get("/health")
    assert response.status_code == 200
```

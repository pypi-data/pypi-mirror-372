# Configuration

## Command Line Parameters

- `--report-html[=PATH]`: Generates HTML report (default: `report.html`)
- `--report-title=TITLE`: Sets custom title for HTML report (default: "Pytest report")
- `--report-json=PATH`: Exports results as JSON file
- `--env-file=PATH`: Loads environment variables from .env file (default: `.env`)

## Command Line Usage Examples

```bash
# Basic parameters
... --report-html=report.html              # HTML report
... --report-json=results.json             # JSON report
... --report-title="API Testing Report"    # Custom report title

# Combining parameters
pytest --report-html=report.html --report-json=results.json

# Using custom .env file
pytest --env-file=staging.env --report-html=staging-report.html

# Running with naming
pytest --report-html=detailed_report.html --report-title="Title"
```

## Configuration via pytest.ini

```ini
[tool:pytest]
addopts = --report-html=report.html --report-title=Title --env-file=.env
```

## Configuration via pyproject.toml

```toml
[tool.pytest.ini_options]
addopts = "--report-html=report.html --report-title=Title --env-file=.env"
```

## Environment Variables

The SDK automatically loads environment variables from `.env` files:

```bash
# .env (default)
API_BASE_URL=https://api.example.com
API_TOKEN=your_secret_token
TIMEOUT=30
DATABASE_URL=postgresql://user:pass@localhost/test
DEBUG=true

# staging.env (for staging environment)
API_BASE_URL=https://staging-api.example.com
API_TOKEN=staging_token_123
TIMEOUT=60
```

Usage in tests

```python
import os
from sdk_pytest_checkmate import HttpClient, step, add_data_report

def test_with_env_variables():
    # Get environment variables
    base_url = os.getenv('API_BASE_URL', 'http://localhost')
    token = os.getenv('API_TOKEN')
    
    with step("Test environment configuration"):
        config = {"base_url": base_url}
    
    with step("HTTP client creation"):
        client = HttpClient(
            base_url,
            headers={"Authorization": f"Bearer {token}"},
        )
    
    with step("API testing"):
        response = client.get("/health")
        assert response.status_code == 200
```

## Markers for Test Organization

The SDK supports special markers for structuring tests:

```python
import pytest

@pytest.mark.epic("API Testing")
@pytest.mark.story("Authentication")
def test_login_api():
    """Regression test for login API"""
    pass

@pytest.mark.epic("Security")
@pytest.mark.story("Authorization")
@pytest.mark.title("SQL injection protection check")
def test_sql_injection_protection():
    """Smoke test for SQL injection protection"""
    pass
```

## Filtering Tests by Markers

```bash
# Run tests for specific epic
pytest -m "epic=='User Management'" --report-html

# Run by story
pytest -m "story=='User Registration'" --report-html
```


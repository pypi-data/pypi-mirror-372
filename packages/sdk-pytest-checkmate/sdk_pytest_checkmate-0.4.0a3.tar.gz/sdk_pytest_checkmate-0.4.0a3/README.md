# sdk-pytest-checkmate

[![PyPI](https://img.shields.io/pypi/v/sdk-pytest-checkmate)](https://pypi.org/project/sdk-pytest-checkmate/)
[![Python](https://img.shields.io/pypi/pyversions/sdk-pytest-checkmate.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A powerful SDK for testing specialists** - advanced pytest-based testing
framework with structured test steps, soft assertions, automatic HTTP logging,
and interactive HTML reports.

## 🎯 Who Is This For?

- **🔧 QA Engineers** - Software quality assurance specialists
- **🤖 Test Automation Engineers** - Test automation specialists  
- **👨‍💻 Developers** - Writing unit and integration tests
- **📋 Test Leads** - Team leaders requiring detailed reporting

## 🌟 Key Features

- 📝 **Structured test steps** - Organize tests into logical, timed blocks
- 🔍 **Soft assertions** - Collect all errors without stopping test execution
- 🌐 **Automatic HTTP reporting** - Track all API requests and responses seamlessly
- 📊 **Interactive HTML reports** - Rich reports with filtering and detailed analysis
- 🔄 **Full async support** - Works with both synchronous and asynchronous tests
- 🛡️ **JSON schema validation** - Validate API responses with soft assertions
- 📋 **Epic/Story organization** - Group tests hierarchically for better management
- 🌍 **Environment management** - Automatic .env file loading and configuration

## 🚀 Quick Start

Installation:

```bash
pip install sdk-pytest-checkmate
```

Create a test file:

```python
import pytest
from sdk_pytest_checkmate import step, soft_assert, HttpClient, add_data_report

@pytest.mark.epic("User Management")
@pytest.mark.story("Authentication")
@pytest.mark.title("User Login Flow")
def test_user_login():
    """Complete user login test with SDK pytest checkmate"""
    client = HttpClient(base_url="https://api.example.com")
    
    with step("Prepare login credentials"):
        credentials = {"username": "testuser", "password": "secure123"}
        add_data_report(credentials, "Login Data")
    
    with step("Attempt user login"):
        response = client.post("/auth/login", json=credentials)
        soft_assert(response.status_code == 200, "Login should be successful")
        soft_assert("token" in response.json(), "Response should contain access token")
    
    with step("Verify user session"):
        profile_response = client.get(
            "/user/profile", 
            headers={"Authorization": f"Bearer {response.json()['token']}"}
        )
        soft_assert(profile_response.status_code == 200, "Profile should be accessible")
        add_data_report(profile_response.json(), "User Profile")
```

Generate your first report:

```bash
pytest --report-html=report.html
```

## 📖 SDK API Functions

- `step(name: str)` - Context manager for creating steps
- `soft_assert(condition, message, details)` - Soft assertion
- `add_data_report(data, label)` - Add data to report
- `HttpClient(base_url, **kwargs)` - HTTP client
- `AsyncHttpClient(base_url, **kwargs)` - Asynchronous HTTP client
- `soft_validate_json(data, schema, schema_path, strict)` - JSON data validation


## 📖 Command Line Options

- `--report-html[=PATH]` - Generate HTML report
- `--report-title=TITLE` - Custom report title  
- `--report-json=PATH` - Export JSON results
- `--env-file=PATH` - Load environment variables

## 📖 Complete Documentation

For comprehensive guides and advanced usage:

- **[📦 Installation Guide](./docs/installation.md)** - Setup and requirements
- **[🎯 Features Overview](./docs/features.md)** - Complete API reference
- **[📊 Reports Guide](./docs/reports.md)** - HTML report features
- **[⚙️ Configuration](./docs/configuration.md)** - Settings and options
- **[❓ FAQ](./docs/faq.md)** - Common questions and troubleshooting

## 🤝 Contributing & Support

- 📖  **[Report Issues](https://github.com/o73k51i/sdk-pytest-checkmate/issues)** - Bug reports and feature requests
- 📖 **[Discussions](https://github.com/o73k51i/sdk-pytest-checkmate/discussions)** - Questions and community support
- 📖 **[Documentation](./docs/main.md)** - Complete documentation index

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built for testing specialists who demand quality, clarity, and comprehensive reporting.** 🚀

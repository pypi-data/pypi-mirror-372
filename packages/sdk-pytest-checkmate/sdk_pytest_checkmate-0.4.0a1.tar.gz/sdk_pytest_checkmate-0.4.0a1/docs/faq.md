# Frequently Asked Questions (FAQ)

## General Questions

### What is sdk-pytest-checkmate?

SDK-pytest-checkmate is a powerful tool for testing specialists, based on pytest. It provides structured test steps, soft assertions, automatic HTTP request reporting, and interactive HTML report generation.

### Is special configuration required?

No, the SDK works "out of the box" after installation. Simply import the functions and use them in tests. To generate reports, add `--report-html=report.html` when running pytest.

### Is it compatible with other pytest plugins?

Yes, the SDK is designed for full compatibility with the pytest ecosystem. It doesn't change the basic pytest logic, only adds additional functionality.

## Installation and Setup

### What are the system requirements?

- Python 3.10, 3.11, 3.12, or 3.13
- pytest ≥ 8.4.1 (installed automatically)
- httpx ≥ 0.28.1 (installed automatically)
- jsonschema ≥ 4.25.1 (installed automatically)

### How to update the SDK?

```bash
# Via pip
pip install --upgrade sdk-pytest-checkmate

# Via uv
uv add sdk-pytest-checkmate --upgrade
```

### How to verify installation?

```bash
# Check SDK presence
pip list | grep sdk-pytest-checkmate

# Check reporting parameters
pytest --help | grep report-html
```

## Functionality

### When to use soft_assert?

Use `soft_assert` when:
- Need to check multiple conditions and see all errors
- Error is not critical for test continuation
- Validating data structure with many fields

Use regular `assert` when:
- Error is critical and test cannot continue
- Need immediate stop at first error

### How does time measurement work?

Time is measured automatically from entry to exit of the context manager. The report shows:
- Step start time
- Step completion time
- Execution duration
- Relative time within the test

## HTTP Client

### Are all HTTP requests logged?

HTTP requests are logged at the `httpx` library level. SDK-pytest-checkmate does not currently use its own logging mechanism. Information about HTTP requests and responses is automatically added to the HTML report, which includes:

- URL and request method
- Request headers
- Request body (JSON, form data, etc.)
- Status code and response headers
- Response body

### Does it work with cookies and sessions?

Yes, cookies are automatically saved between requests within one client:

```python
client = HttpClient("https://example.com")
# First request sets cookies
response1 = client.get("/login")
# Subsequent requests automatically use cookies
response2 = client.get("/profile")
```

## Reports

### Can the appearance be customized?

The HTML report has a fixed design, but supports:
- Dark/light theme
- Filtering by markers and status

### How to share the report?

The HTML report is a self-contained file:
- Send via email
- Upload to shared drive
- Publish on web server

## Performance

### Does the SDK affect test speed?

The impact is minimal:
- Step time measurement: microseconds
- HTTP reporting: milliseconds
- Report generation: seconds at the end

## Errors and Debugging

### Tests fail with ImportError

```bash
# Check installation
pip list | grep sdk-pytest-checkmate

# Reinstall
pip uninstall sdk-pytest-checkmate
pip install sdk-pytest-checkmate
```

### HTML report is not generated

Possible causes:
- `--report-html` parameter not specified
- No write permissions to directory
- pytest terminated with error before report generation

### Data not displayed in report

```python
# ✅ Correct - JSON-serializable data
add_data_report({"key": "value"}, "Data")
add_data_report(obj.__dict__, "Object Data")

# ❌ Incorrect - non-serializable objects
add_data_report(complex_object, "Data")  # May not display
```

## Contributing to Development

### How to report a bug?

1. Check [existing issues](https://github.com/o73k51i/sdk-pytest-checkmate/issues)
2. Create a new issue with:
   - Detailed problem description
   - Minimal example to reproduce
   - Python, pytest, and SDK versions

### How to suggest improvements?

1. Create an issue describing the feature
2. Explain the use case and benefits
3. Create a pull request (optional)

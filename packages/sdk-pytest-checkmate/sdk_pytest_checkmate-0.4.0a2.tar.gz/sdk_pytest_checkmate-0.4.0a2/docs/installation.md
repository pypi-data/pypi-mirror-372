# Installation

## Technical Requirements

- **Python:** 3.10, 3.11, 3.12, 3.13
- **Core Dependencies:**
  - pytest ≥ 8.4.1
  - httpx ≥ 0.28.1 (for HTTP client)
  - jsonschema ≥ 4.25.1 (for JSON validation)
  - pytest-asyncio ≥ 1.1.0 (for async tests)

## Installation via pip

```bash
pip install sdk-pytest-checkmate
```

All necessary dependencies will be installed automatically.

## Installation via uv

```bash
uv add sdk-pytest-checkmate
```

UV will automatically install compatible versions of all dependencies.

## Installation Verification

```bash
pytest --help | grep report-html
```

You should see the `--report-html` option in the list of available parameters.

## Basic Configuration

The SDK works automatically after installation and importing functions. To generate an HTML report, simply add the parameter when running tests:

```bash
pytest --report-html=report.html
```

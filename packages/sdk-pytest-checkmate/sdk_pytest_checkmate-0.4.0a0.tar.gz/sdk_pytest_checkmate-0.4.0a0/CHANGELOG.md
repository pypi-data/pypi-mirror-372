# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Add a client for working with databases
- Improve HTTP client handling (hide sensitive data)
- Improve HTML report

## [0.4.0a0] - 2025-08-28

### Added
- **JSON Schema Validation**: `soft_validate_json()` function for non-fatal JSON schema validation with detailed error reporting
  - Support for inline schema dictionaries and external schema files
  - Strict mode option for raising exceptions instead of soft assertions
  - Comprehensive error formatting with path information
  - Integration with soft assertions for test continuity
- **Asynchronous HTTP Client**: Enhanced `AsyncHttpClient` class for async API testing
  - Automatic request/response reporting to HTML reports
  - Context manager support for proper resource cleanup
  - Full compatibility with httpx AsyncClient features
- **Enhanced HTTP Client Architecture**: 
  - Refactored `HttpClient` and `AsyncHttpClient` as primary classes
  - Removed deprecated `create_http_client()` and `async_create_http_client()` functions
  - Improved class-based API for better type safety and extensibility
- **Enhanced Soft Assertions**:
  - Optional `details` parameter for `soft_assert()` function
  - Support for custom debugging information
  - Improved condition evaluation and error reporting
  - Better integration with test reporting system
- **Comprehensive Documentation Suite**:
  - Complete documentation structure in `docs/` directory
  - Installation guide with technical requirements
  - Feature documentation with SDK API references
  - Configuration guide for command-line parameters
  - FAQ covering common questions and troubleshooting
  - Reports documentation for HTML generation
  - Main documentation with quick start examples

### Enhanced
- **HTML Report Generation**:
  - Added test statistics overview for better test result analysis
  - Custom title and parameter ID support in test results
  - Enhanced detail view with test function names
  - Improved parameter display for parametrized tests
  - Better visual organization of test data
- **Test Organization**:
  - Enhanced parametrize test naming for better identification
  - Improved test structure across all test modules
  - Better type hints and documentation in test files
  - Clearer test function organization and naming
- **Code Quality**:
  - Comprehensive type hints across all modules
  - Enhanced docstrings for better code documentation
  - Improved error handling and validation
  - Better separation of concerns in module architecture

### Refactored
- **Module Architecture**: Complete refactoring of core modules for better maintainability
  - `_core.py`: Enhanced step and soft assertion management
  - `_http_client.py`: Class-based HTTP client implementation
  - `_json_validator.py`: New module for JSON schema validation
  - `_plugin.py`: Improved pytest plugin integration
  - `_report_generator.py`: Enhanced HTML report generation
- **Import Structure**: Streamlined module exports in `__init__.py`
  - Primary exports: `HttpClient`, `AsyncHttpClient`, `soft_validate_json`
  - Maintained backward compatibility for existing functions
  - Removed unused internal function exports
- **Test Suite**: Comprehensive refactoring of test modules
  - Enhanced type safety with proper type hints
  - Improved test documentation and structure
  - Better test organization and naming conventions

### Fixed
- **Session Management**: Fixed attribute access for checkmate start time in pytest session finish
- **Plugin Integration**: Improved pytest plugin compatibility and error handling
- **Report Generation**: Enhanced stability and error handling in HTML report creation

### Documentation
- **Project Description**: Updated package description to "Advanced pytest-based testing framework for QA engineers and test automation specialists"
- **Enhanced Keywords**: Expanded keyword list to include comprehensive testing and automation terms
- **Documentation Links**: Updated documentation URL to point to structured docs in `docs/main.md`
- **README**: Comprehensive refactoring with updated examples and usage patterns

### Technical Details
- **Dependencies**: Added `jsonschema>=4.25.1` for JSON schema validation support
- **Code Quality**: Enhanced linting configuration and code formatting standards
- **Type Safety**: Improved type annotations
- **Performance**: Optimized report generation and data handling

### Breaking Changes
- Removed `create_http_client()` and `async_create_http_client()` functions (use `HttpClient` and `AsyncHttpClient` classes instead)
- Function signature changes in some internal APIs (public API remains compatible)

### Migration Guide
- Replace `create_http_client(url)` with `HttpClient(url)`
- Replace `async_create_http_client(url)` with `AsyncHttpClient(url)`
- Update imports to use new class-based HTTP clients
=======
## [0.4.0a0] - 2025-08-26

### Added
- `soft_validator_json()` function for non-fatal JSON schema validation with detailed error reporting

## [0.3.0a6] - 2025-08-25

### Added
- **Environment Variables Support**: Automatic loading of environment variables from `.env` files
- New command line option `--env-file=PATH` to specify custom .env file path (default: `.env`)
- Example `.env.example` file with common configuration patterns for API endpoints, database settings, feature flags, and test data
- Environment variable documentation in README with usage examples and best practices

### Enhanced
- Comprehensive documentation updates with environment variable usage examples across README and module docstrings
- Quick Start guide updated with environment-specific testing examples
- Plugin documentation enhanced with .env file loading details and command-line usage

### Internal
- Added test coverage for environment variable functionality
- Enhanced error handling for .env file loading with graceful fallbacks

### Documentation
- Added detailed environment variables section in README
- Updated command-line options documentation
- Enhanced examples showing integration with environment-specific configurations
- Improved module docstrings with environment variable usage patterns

## [0.2.0a6] - 2025-08-24

### Added
- `create_http_client()` function for enhanced HTTP testing with automatic request/response logging
- Complete module docstrings for improved code documentation
- Enhanced API documentation in README with HTTP client examples

### Changed
- Updated module `__init__.py` with comprehensive documentation including HTTP client usage examples
- Improved code documentation across all modules with detailed docstrings for classes and functions

### Internal
- Modified test modules to verify functionality

## [0.1.0a4] - 2025-08-19

### Changed
- Revised versioning approach: switched to 0.0.0aN pre-release tag pattern to better reflect early, unstable iteration cadence before first public minor (0.1.0).

### Added
- Display of pytest parametrization values in HTML report: each parametrized test invocation now shows its parameters inline in the test title (e.g. `Test with parametrize [id=2]`), improving traceability when multiple variants run.

### Internal
- No functional logic changes besides exposing collected `callspec.params` in results payload.

## [0.0.3a] - 2025-08-19

### Added
- Dark theme styling for HTML report.
- Theme toggle button (floating) with localStorage persistence across sessions.

## [0.0.2a] - 2025-08-19

### Changed
- HTML report footer simplified: removed display of raw invocation arguments (`Args:`) for a cleaner UI and to avoid leaking local run context.

### Fixed
- Data attachments (`add_data_report`) now stay within the detail card: long / wide JSON or string payloads are wrapped (`white-space: pre-wrap`, `word-break: break-word`) and constrained with a scrollable area (`max-height: 340px`) preventing horizontal page overflow.

## [0.0.1a] - 2025-08-18

### Added
- Initial alpha release of sdk-pytest-checkmate plugin
- **Core Features:**
  - `step(name)` context manager for recording test steps with timing
  - `soft_assert(condition, message)` for non-fatal assertions
  - `add_data_report(data, label)` for attaching arbitrary data to test timeline
- **Pytest Markers:**
  - `@pytest.mark.title(name)` for custom test titles
  - `@pytest.mark.epic(name)` for epic-level test grouping
  - `@pytest.mark.story(name)` for story-level test grouping
- **HTML Reporting:**
  - Rich interactive HTML reports with timeline view
  - Expandable/collapsible epic and story sections
  - Inline data inspection with JSON pretty-printing
  - Status filtering (PASSED, FAILED, SKIPPED, etc.)
  - Step timing and error tracking
  - Soft assertion failure aggregation
- **Command Line Options:**
  - `--report-html[=PATH]` to generate HTML reports
  - `--report-title=TITLE` to customize report title
  - `--report-json=PATH` to export results as JSON
- **Async Support:**
  - Context managers work with both `with` and `async with`
  - Full support for async test functions
- **Type Safety:**
  - Full type hints with `py.typed` marker
  - Compatible with mypy and other type checkers
- **Python Compatibility:**
  - Python 3.10+ support
  - pytest 8.4.1+ compatibility

### Technical Details
- Built with modern Python features (union types, dataclasses)
- Uses pytest's StashKey for test data storage
- Context variables for thread-safe test isolation
- Comprehensive error handling and validation
- JSON serialization for data portability

### Documentation
- Complete README with examples and API reference
- Detailed docstrings for all public functions
- Type annotations for LSP support
- Installation and usage instructions

### Testing
- Comprehensive test suite with 36+ test cases
- Unit tests for all core functionality
- Integration tests for combined features
- Marker functionality tests
- Performance testing for large datasets

### Known Limitations
- Requires Python 3.10+ due to union type syntax
- Large data attachments may impact report size
- HTML reports require modern browsers for full functionality

---

## Version History Legend

- **Added** for new features
- **Changed** for changes in existing functionality  
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Links

- [GitHub Repository](https://github.com/o73k51i/sdk-pytest-checkmate)
- [PyPI Package](https://pypi.org/project/sdk-pytest-checkmate/)
- [Issue Tracker](https://github.com/o73k51i/sdk-pytest-checkmate/issues)

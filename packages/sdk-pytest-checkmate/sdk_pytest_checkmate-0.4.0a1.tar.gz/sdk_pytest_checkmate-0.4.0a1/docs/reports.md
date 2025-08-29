# Reports

## HTML Report Generation

To create an HTML report, use the `--report-html` parameter when running
tests written with the SDK:

```bash
pytest --report-html=report.html
```

## Additional Reporting Parameters

```bash
# Generate JSON report along with HTML
pytest --report-html=report.html --report-json=results.json

# Run with additional options
pytest -v --report-html=detailed_report.html
```

## Report Structure

The HTML report contains:

- **General statistics** - number of passed/failed tests
- **Status filtering** - PASSED, FAILED, ERROR, SKIPPED, XFAIL, XPASS
- **Marker filtering** - epic, story, smoke, regression, etc.
- **Error details** - stack trace and error messages
- **HTTP requests** - complete information about API calls with headers and body
- **Attached data** - JSON data from tests in a readable format
- **Soft assertions** - list of all soft_assert with results

## Interactive Features

- **Expand/collapse** test details for convenient viewing
- **View attached data** in formatted JSON view
- **Dark/light theme** for comfortable viewing
- **Export results** to JSON format for further processing

## Report Configuration

```bash
# Custom report title
pytest --report-title="API Tests v2.1" --report-html=api-tests.html

# Generate both formats
pytest --report-html=full-report.html --report-json=results.json
```

"""Pytest plugin for sdk_pytest_checkmate."""

from __future__ import annotations

import contextlib
import time
from collections.abc import Generator

import pytest

from ._config import add_pytest_options, configure_pytest_markers, load_env_file
from ._context import STASH_RESULTS
from ._types import AnyType, TestContext


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add checkmate-specific command line options to pytest.

    Args:
        parser: The pytest argument parser.
    """
    add_pytest_options(parser)


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with checkmate-specific settings.

    Args:
        config: The pytest configuration object.
    """
    configure_pytest_markers(config)
    config.stash[STASH_RESULTS] = []
    config.checkmate_start_time = time.time()  # type: ignore[attr-defined]

    env_file = config.getoption("env_file")
    if env_file:
        load_env_file(env_file)


@pytest.fixture(autouse=True)
def _checkmate_context() -> Generator[TestContext, None, None]:
    """Provide test context for each test execution.

    Yields:
        Test context dictionary containing steps, checks, and data reports.
    """
    from ._context import _ACTIVE_CONTEXT

    ctx: TestContext = {
        "steps": [],
        "soft_failures": [],
        "soft_checks": [],
        "data_reports": [],
        "seq": 0,
    }
    token = _ACTIVE_CONTEXT.set(ctx)
    try:
        yield ctx
    finally:
        _ACTIVE_CONTEXT.reset(token)


def _should_record_test_result(rep: object) -> bool:
    """Determine if test result should be recorded based on test phase and outcome.

    Args:
        rep: Test report object.

    Returns:
        True if the test result should be recorded.
    """
    return (
        rep.when == "call"  # type: ignore[attr-defined]
        or (rep.when == "setup" and (rep.skipped or rep.failed))  # type: ignore[attr-defined]
        or (rep.when == "teardown" and rep.failed)  # type: ignore[attr-defined]
    )


def _determine_test_status(rep: object) -> str:
    """Determine test status from test report.

    Args:
        rep: Test report object.

    Returns:
        Test status string (PASSED, FAILED, ERROR, SKIPPED, XFAIL, XPASS).
    """
    if rep.skipped:  # type: ignore[attr-defined]
        return "XFAIL" if getattr(rep, "wasxfail", False) else "SKIPPED"
    if rep.failed:  # type: ignore[attr-defined]
        return "XFAIL" if getattr(rep, "wasxfail", False) else ("FAILED" if rep.when == "call" else "ERROR")  # type: ignore[attr-defined]
    if rep.passed:  # type: ignore[attr-defined]
        return "XPASS" if getattr(rep, "wasxfail", False) else "PASSED"
    return rep.outcome.upper()  # type: ignore[attr-defined]


def _extract_test_metadata(item: pytest.Item) -> tuple[str, str | None, str | None]:
    """Extract test metadata (title, epic, story) from test item markers.

    Args:
        item: Pytest test item.

    Returns:
        Tuple of (title, epic, story).
    """
    title_marker = item.get_closest_marker("title")
    title = title_marker.args[0] if title_marker and title_marker.args else item.name

    epic_marker = item.get_closest_marker("epic")
    epic = epic_marker.args[0] if epic_marker and epic_marker.args else None

    story_marker = item.get_closest_marker("story")
    story = story_marker.args[0] if story_marker and story_marker.args else None

    return title, epic, story


def _format_test_details(rep: object, status: str) -> tuple[str, str]:
    """Format detailed error/failure information from test report.

    Args:
        rep: Test report object.
        status: Test status string.

    Returns:
        Tuple of (full_details, short_details).
    """
    full_details = ""
    short_details = ""

    if (status in {"XFAIL", "XPASS"}) and getattr(rep, "wasxfail", None):
        reason = str(getattr(rep, "wasxfail", ""))
        short_details = full_details = reason
    elif rep.failed or rep.outcome == "failed":  # type: ignore[attr-defined]
        full_details = str(rep.longrepr) if rep.longrepr else ""  # type: ignore[attr-defined]
        if full_details.startswith("Soft assertion failures"):
            short_details = full_details
        else:
            lines = full_details.splitlines()
            short_details = next(
                (ln[2:].strip() for ln in lines if ln.startswith("E ")),
                "",
            )
            if not short_details and lines:
                short_details = lines[-1].strip()
    elif rep.skipped:  # type: ignore[attr-defined]
        full_details = (
            rep.longrepr[2]  # type: ignore[attr-defined]
            if isinstance(rep.longrepr, tuple)  # type: ignore[attr-defined]
            else str(rep.longrepr)  # type: ignore[attr-defined]
            if rep.longrepr  # type: ignore[attr-defined]
            else ""  # type: ignore[attr-defined]
        )
        short_details = full_details

    return full_details, short_details


def _get_test_context_data(item: pytest.Item) -> tuple[list[object], list[object], list[object]]:
    """Get test context data (steps, soft_checks, data_reports) from item stash.

    Args:
        item: Pytest test item.

    Returns:
        Tuple of (steps, soft_checks, data_reports) lists.
    """
    from ._context import STASH_CTX

    ctx = item.stash.get(STASH_CTX, None)
    steps = ctx["steps"] if ctx else []
    soft_checks = ctx["soft_checks"] if ctx else []
    data_reports = ctx["data_reports"] if ctx else []

    return steps, soft_checks, data_reports


def _create_test_result_dict(
    item: pytest.Item,
    rep: object,
    title: str,
    status: str,
    full_details: str,
    short_details: str,
    steps: list[object],
    soft_checks: list[object],
    data_reports: list[object],
    epic: str | None,
    story: str | None,
) -> dict[str, object]:
    """Create test result dictionary for storage.

    Args:
        item: Pytest test item.
        rep: Test report object.
        title: Test title.
        status: Test status.
        full_details: Full error details.
        short_details: Short error summary.
        steps: List of test steps.
        soft_checks: List of soft assertions.
        data_reports: List of data attachments.
        epic: Epic marker value.
        story: Story marker value.

    Returns:
        Dictionary containing complete test result data.
    """
    from ._models import DataRecord, SoftCheckRecord, StepRecord

    return {
        "name": item.nodeid,
        "title": title,
        "status": status,
        "duration": rep.duration,  # type: ignore[attr-defined]
        "short": short_details,
        "full": full_details,
        "steps": [s.to_dict() if isinstance(s, StepRecord) else s for s in steps],
        "soft_checks": [sc.to_dict() if isinstance(sc, SoftCheckRecord) else sc for sc in soft_checks],
        "data_reports": [dr.to_dict() if isinstance(dr, DataRecord) else dr for dr in data_reports],
        "epic": epic,
        "story": story,
        "has_custom_title": item.get_closest_marker("title") is not None,
        "params": {
            k: repr(v)
            for k, v in getattr(
                getattr(item, "callspec", None),
                "params",
                {},
            ).items()
        },
        "param_id": getattr(
            getattr(item, "callspec", None),
            "id",
            None,
        ),
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, None, None]:  # noqa: ARG001
    """Generate test reports with checkmate-specific data collection.

    This hook collects test execution data including steps, soft assertions,
    and data attachments, then formats them into structured test results.

    Args:
        item: Pytest test item being executed.
        call: Call information (unused but required by pytest).

    Yields:
        Test report with enhanced checkmate data.
    """
    from ._context import STASH_CTX, get_context

    outcome = yield
    rep = outcome.get_result()  # type: ignore[attr-defined]

    if rep.when == "setup":  # type: ignore[attr-defined]
        with contextlib.suppress(RuntimeError):
            item.stash[STASH_CTX] = get_context()

    if rep.when == "call":  # type: ignore[attr-defined]
        ctx = item.stash.get(STASH_CTX, None)
        if ctx and ctx["soft_failures"] and rep.passed:  # type: ignore[attr-defined]
            lines = [f"Soft assertion failures ({len(ctx['soft_failures'])}):"] + [
                f" {i + 1}. {m}" for i, m in enumerate(ctx["soft_failures"])
            ]
            rep.outcome = "failed"  # type: ignore[attr-defined]
            rep.longrepr = "\n".join(lines)  # type: ignore[attr-defined]

    if not _should_record_test_result(rep):
        return

    status = _determine_test_status(rep)
    title, epic, story = _extract_test_metadata(item)
    full_details, short_details = _format_test_details(rep, status)
    steps, soft_checks, data_reports = _get_test_context_data(item)

    test_result = _create_test_result_dict(
        item,
        rep,
        title,
        status,
        full_details,
        short_details,
        steps,
        soft_checks,
        data_reports,
        epic,
        story,
    )

    item.config.stash[STASH_RESULTS].append(test_result)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    """Generate HTML and JSON reports at the end of the test session.

    Args:
        session: Pytest session object.
        exitstatus: Test session exit status (unused).
    """
    from pathlib import Path

    from ._report_generator import generate_html_report, save_json_report

    config = session.config
    report_opt = config.getoption("report_html")
    if not report_opt:
        return

    results: list[dict[str, AnyType]] = config.stash.get(STASH_RESULTS, [])
    if not results:
        return

    start_ts = getattr(config, "checkmate_start_time", None)
    end_ts = time.time()
    title_opt = config.getoption("report_title") or "Pytest report"
    json_path_opt = config.getoption("report_json")
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")

    if json_path_opt:
        success = save_json_report(results, json_path_opt)
        if not success and terminal:
            terminal.write_line(
                f"checkmate: failed to write JSON report '{json_path_opt}'",
            )

    report_path = (
        (session.config.rootpath / report_opt)
        if isinstance(report_opt, str)
        else (session.config.rootpath / "report.html")
    )
    report_path = Path(report_path)

    success = generate_html_report(
        results,
        title_opt,
        start_ts or 0.0,
        end_ts,
        report_path,
    )

    if success and terminal:
        terminal.write_line(f"Checkmate HTML report to file://{report_path}")
    elif not success and terminal:
        terminal.write_line(f"checkmate: failed to write HTML report '{report_path}'")
